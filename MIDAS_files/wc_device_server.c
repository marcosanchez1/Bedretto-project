/**
 * WaveCatcher Device Server - Persistent device owner process
 * 
 * This server:
 * - Opens WaveCatcher device once at startup (tolerates long blocking)
 * - Keeps device open continuously  
 * - Accepts configuration commands via Unix socket
 * - Provides event readout on demand
 * - Allows MIDAS frontend to reconfigure without reopening hardware
 * 
 * Communication protocol (simple text-based over Unix socket):
 *   Client -> Server:
 *     CONFIGURE <json_params>
 *     START_RUN
 *     STOP_RUN  
 *     READ_EVENT
 *     GET_STATUS
 *     SHUTDOWN
 *   Server -> Client:
 *     OK <json_response>
 *     ERROR <message>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <errno.h>
#include <signal.h>
#include <poll.h>
#include <time.h>
#include "WaveCat64ch_Lib.h"

#define SOCKET_PATH "/tmp/wc_device_server.sock"
#define MAX_CLIENTS 4
#define BUFFER_SIZE 65536

// Server state
static int g_device_open = 0;
static int g_run_active = 0;
static WAVECAT64CH_EventStruct g_evt = {0};
static int g_evt_allocated = 0;
static int g_shutdown_requested = 0;

// Configuration state (mirrors ODB structure)
static struct {
    int enabled_channel;
    float trigger_threshold_v;
    int trigger_edge; // 0=pos, 1=neg
    int trigger_mode; // 0=normal, 1=software, 2=coincidence
    int sw_trigger_hz;
    int coincidence_channel;
    float coincidence_threshold_v;
} g_config = {0, 0.030f, 0, 0, 0, 1, 0.050f};

static void log_msg(const char *fmt, ...) {
    char timestamp[64];
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", tm_info);
    
    printf("[%s] ", timestamp);
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
    printf("\n");
    fflush(stdout);
}

static int wc_check(WAVECAT64CH_ErrCode code, const char *where) {
    if (code == WAVECAT64CH_Success) return 0;
    log_msg("ERROR: %s failed with code %d", where, (int)code);
    return -1;
}

static int device_open() {
    if (g_device_open) {
        log_msg("Device already open");
        return 0;
    }
    
    log_msg("Opening WaveCatcher device (this may block for 15-300 seconds)...");
    int handle = -1;
    for (int attempt = 1; attempt <= 6; ++attempt) {
        log_msg("OpenDevice attempt %d/6", attempt);
        if (wc_check(WAVECAT64CH_OpenDevice(&handle), "OpenDevice") == 0) {
            log_msg("Device opened successfully on attempt %d", attempt);
            g_device_open = 1;
            break;
        }
        usleep(200000); // 200ms
    }
    
    if (!g_device_open) {
        log_msg("ERROR: Failed to open device after 6 attempts");
        return -1;
    }
    
    if (wc_check(WAVECAT64CH_ResetDevice(), "ResetDevice") != 0) return -1;
    if (wc_check(WAVECAT64CH_SetDefaultParameters(), "SetDefaultParameters") != 0) return -1;
    
    log_msg("Device initialized and ready");
    return 0;
}

static int apply_configuration() {
    if (!g_device_open) {
        log_msg("ERROR: Cannot configure - device not open");
        return -1;
    }
    
    log_msg("Applying configuration: ch=%d thr=%.3fV edge=%d mode=%d",
            g_config.enabled_channel, g_config.trigger_threshold_v, 
            g_config.trigger_edge, g_config.trigger_mode);
    
    // Enable primary channel
    if (wc_check(WAVECAT64CH_SetChannelState(WAVECAT64CH_FRONT_CHANNEL, 
                                               g_config.enabled_channel, 
                                               WAVECAT64CH_STATE_ON), "SetChannelState") != 0)
        return -1;
    
    // Configure trigger
    if (wc_check(WAVECAT64CH_SetTriggerSourceState(g_config.enabled_channel, 
                                                     WAVECAT64CH_TRIG_ON), "SetTriggerSourceState") != 0)
        return -1;
    
    WAVECAT64CH_TriggerEdgeType edge = (g_config.trigger_edge == 0) ? 
                                        WAVECAT64CH_POS_EDGE : WAVECAT64CH_NEG_EDGE;
    if (wc_check(WAVECAT64CH_SetTriggerEdge(g_config.enabled_channel, edge), "SetTriggerEdge") != 0)
        return -1;
    
    if (wc_check(WAVECAT64CH_SetTriggerThreshold(g_config.enabled_channel, 
                                                   g_config.trigger_threshold_v), "SetTriggerThreshold") != 0)
        return -1;
    
    // Set trigger mode
    WAVECAT64CH_TriggerModeType tmode = (g_config.trigger_mode == 1) ?
                                         WAVECAT64CH_SOFTWARE_TRIG : WAVECAT64CH_NORMAL_TRIG;
    if (wc_check(WAVECAT64CH_SetTriggerMode(tmode), "SetTriggerMode") != 0)
        return -1;
    
    // Coincidence mode (if enabled)
    if (g_config.trigger_mode == 2) {
        if (wc_check(WAVECAT64CH_SetChannelState(WAVECAT64CH_FRONT_CHANNEL,
                                                   g_config.coincidence_channel,
                                                   WAVECAT64CH_STATE_ON), "SetChannelState(coinc)") != 0)
            return -1;
        if (wc_check(WAVECAT64CH_SetTriggerSourceState(g_config.coincidence_channel,
                                                         WAVECAT64CH_TRIG_ON), "SetTriggerSourceState(coinc)") != 0)
            return -1;
        if (wc_check(WAVECAT64CH_SetTriggerThreshold(g_config.coincidence_channel,
                                                       g_config.coincidence_threshold_v), "SetTriggerThreshold(coinc)") != 0)
            return -1;
    }
    
    if (wc_check(WAVECAT64CH_PrepareEvent(), "PrepareEvent") != 0) return -1;
    
    log_msg("Configuration applied successfully");
    return 0;
}

static int start_run() {
    if (!g_device_open) {
        log_msg("ERROR: Cannot start run - device not open");
        return -1;
    }
    if (g_run_active) {
        log_msg("WARNING: Run already active");
        return 0;
    }
    
    if (!g_evt_allocated) {
        if (wc_check(WAVECAT64CH_AllocateEventStructure(&g_evt), "AllocateEventStructure") != 0)
            return -1;
        g_evt_allocated = 1;
    }
    
    if (wc_check(WAVECAT64CH_StartRun(), "StartRun") != 0) return -1;
    
    g_run_active = 1;
    log_msg("Run started");
    return 0;
}

static int stop_run() {
    if (!g_run_active) {
        log_msg("WARNING: No run active");
        return 0;
    }
    
    if (wc_check(WAVECAT64CH_StopRun(), "StopRun") != 0) {
        log_msg("WARNING: StopRun returned error (continuing anyway)");
    }
    
    g_run_active = 0;
    log_msg("Run stopped");
    return 0;
}

static int read_event(char *response_buf, size_t buf_size) {
    if (!g_run_active) {
        snprintf(response_buf, buf_size, "ERROR No run active");
        return -1;
    }
    
    WAVECAT64CH_ErrCode ec = WAVECAT64CH_ReadEventBuffer();
    if (ec == WAVECAT64CH_EvtNotReady || ec == WAVECAT64CH_NoEvent) {
        snprintf(response_buf, buf_size, "OK NO_EVENT");
        return 0;
    }
    if (ec != WAVECAT64CH_Success && ec != WAVECAT64CH_Incomplete) {
        snprintf(response_buf, buf_size, "ERROR ReadEventBuffer=%d", (int)ec);
        return -1;
    }
    
    ec = WAVECAT64CH_DecodeEvent(&g_evt);
    if (ec != WAVECAT64CH_Success) {
        snprintf(response_buf, buf_size, "ERROR DecodeEvent=%d", (int)ec);
        return -1;
    }
    
    // Read channel data
    WAVECAT64CH_ChannelDataStruct cdata = {0};
    ec = WAVECAT64CH_ReadChannelDataStruct(g_config.enabled_channel, &cdata);
    if (ec != WAVECAT64CH_Success) {
        snprintf(response_buf, buf_size, "ERROR ReadChannelDataStruct=%d", (int)ec);
        return -1;
    }
    
    // Format response with basic event info
    snprintf(response_buf, buf_size, 
             "OK EVENT ch=%d samples=%d trig_cell=%d",
             g_config.enabled_channel, (int)cdata.iNumSamples, (int)cdata.iTriggerCell);
    
    return 0;
}

static void handle_client_command(const char *cmd, char *response, size_t response_size) {
    log_msg("Command: %s", cmd);
    
    if (strncmp(cmd, "CONFIGURE ", 10) == 0) {
        // Parse simple key=value pairs (JSON parsing would be better for production)
        const char *params = cmd + 10;
        sscanf(params, "ch=%d thr=%f edge=%d mode=%d sw_hz=%d coinc_ch=%d coinc_thr=%f",
               &g_config.enabled_channel, &g_config.trigger_threshold_v,
               &g_config.trigger_edge, &g_config.trigger_mode,
               &g_config.sw_trigger_hz, &g_config.coincidence_channel,
               &g_config.coincidence_threshold_v);
        
        if (apply_configuration() == 0) {
            snprintf(response, response_size, "OK configured");
        } else {
            snprintf(response, response_size, "ERROR configuration failed");
        }
    }
    else if (strcmp(cmd, "START_RUN") == 0) {
        if (start_run() == 0) {
            snprintf(response, response_size, "OK run_started");
        } else {
            snprintf(response, response_size, "ERROR start_run failed");
        }
    }
    else if (strcmp(cmd, "STOP_RUN") == 0) {
        if (stop_run() == 0) {
            snprintf(response, response_size, "OK run_stopped");
        } else {
            snprintf(response, response_size, "ERROR stop_run failed");
        }
    }
    else if (strcmp(cmd, "READ_EVENT") == 0) {
        read_event(response, response_size);
    }
    else if (strcmp(cmd, "GET_STATUS") == 0) {
        snprintf(response, response_size, "OK device_open=%d run_active=%d",
                 g_device_open, g_run_active);
    }
    else if (strcmp(cmd, "SHUTDOWN") == 0) {
        g_shutdown_requested = 1;
        snprintf(response, response_size, "OK shutting_down");
    }
    else {
        snprintf(response, response_size, "ERROR unknown_command");
    }
}

static void cleanup() {
    log_msg("Cleaning up...");
    if (g_run_active) {
        WAVECAT64CH_StopRun();
        g_run_active = 0;
    }
    if (g_evt_allocated) {
        WAVECAT64CH_FreeEventStructure(&g_evt);
        g_evt_allocated = 0;
    }
    if (g_device_open) {
        WAVECAT64CH_CloseDevice();
        g_device_open = 0;
    }
    unlink(SOCKET_PATH);
    log_msg("Cleanup complete");
}

static void signal_handler(int sig) {
    log_msg("Received signal %d, shutting down", sig);
    g_shutdown_requested = 1;
}

int main(int argc, char **argv) {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    log_msg("WaveCatcher Device Server starting...");
    
    // Open device (this can block for a long time - that's OK, we're not in MIDAS yet)
    if (device_open() != 0) {
        log_msg("FATAL: Cannot open device");
        return 1;
    }
    
    // Create Unix socket
    unlink(SOCKET_PATH); // Remove old socket if exists
    int listen_sock = socket(AF_UNIX, SOCK_STREAM, 0);
    if (listen_sock < 0) {
        log_msg("FATAL: Cannot create socket: %s", strerror(errno));
        cleanup();
        return 1;
    }
    
    struct sockaddr_un addr = {0};
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);
    
    if (bind(listen_sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        log_msg("FATAL: Cannot bind socket: %s", strerror(errno));
        close(listen_sock);
        cleanup();
        return 1;
    }
    
    if (listen(listen_sock, MAX_CLIENTS) < 0) {
        log_msg("FATAL: Cannot listen: %s", strerror(errno));
        close(listen_sock);
        cleanup();
        return 1;
    }
    
    log_msg("Device server ready on %s", SOCKET_PATH);
    log_msg("Waiting for connections...");
    
    // Simple single-client server (production would use select/poll for multiple clients)
    while (!g_shutdown_requested) {
        struct pollfd pfd = {listen_sock, POLLIN, 0};
        int ret = poll(&pfd, 1, 1000); // 1s timeout for shutdown check
        
        if (ret < 0) {
            if (errno == EINTR) continue;
            log_msg("ERROR: poll failed: %s", strerror(errno));
            break;
        }
        if (ret == 0) continue; // Timeout
        
        int client_sock = accept(listen_sock, NULL, NULL);
        if (client_sock < 0) {
            log_msg("ERROR: accept failed: %s", strerror(errno));
            continue;
        }
        
        log_msg("Client connected");
        
        // Handle client commands
        char cmd_buf[BUFFER_SIZE];
        char response_buf[BUFFER_SIZE];
        
        while (!g_shutdown_requested) {
            ssize_t n = recv(client_sock, cmd_buf, sizeof(cmd_buf) - 1, 0);
            if (n <= 0) break;
            
            cmd_buf[n] = '\0';
            // Strip newline
            char *nl = strchr(cmd_buf, '\n');
            if (nl) *nl = '\0';
            
            handle_client_command(cmd_buf, response_buf, sizeof(response_buf));
            
            strcat(response_buf, "\n");
            send(client_sock, response_buf, strlen(response_buf), 0);
            
            if (g_shutdown_requested) break;
        }
        
        close(client_sock);
        log_msg("Client disconnected");
    }
    
    close(listen_sock);
    cleanup();
    log_msg("Device server exited");
    return 0;
}
