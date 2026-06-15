/**
 * WaveCatcher Device Keeper - Ultra-minimal persistent device owner
 * 
 * This tiny server:
 * - Opens WaveCatcher device ONCE at startup (tolerates long blocking)
 * - Keeps it open forever
 * - Does NOTHING else - just holds the device open
 * - MIDAS frontend inherits the open device via environment
 * 
 * Why this works:
 * - OpenDevice blocking happens BEFORE MIDAS stack starts (no RPC timeouts)
 * - Once open, device stays open (no re-opening between runs)
 * - MIDAS frontend can still call all config/run APIs on the already-open device
 * - Device is a singleton - only one process can open it, so frontend reuses it
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include "WaveCat64ch_Lib.h"

static int g_device_open = 0;
static int g_shutdown_requested = 0;

static void log_msg(const char *fmt, ...) {
    char timestamp[64];
    time_t now = time(NULL);
    struct tm *tm_info = localtime(now);
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", tm_info);
    
    printf("[%s] ", timestamp);
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
    printf("\n");
    fflush(stdout);
}

static void signal_handler(int sig) {
    log_msg("Received signal %d, shutting down", sig);
    g_shutdown_requested = 1;
}

int main(int argc, char **argv) {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    log_msg("=== WaveCatcher Device Keeper ===");
    log_msg("This process will open the device and hold it open");
    log_msg("MIDAS frontend will inherit access to the open device");
    log_msg("Press Ctrl+C to close device and exit");
    log_msg("");
    
    // Open device (this can block for 15-300 seconds - that's OK, we're standalone)
    log_msg("Opening WaveCatcher device (may block 15-300 seconds)...");
    
    int handle = -1;
    for (int attempt = 1; attempt <= 10; ++attempt) {
        log_msg("OpenDevice attempt %d/10...", attempt);
        WAVECAT64CH_ErrCode ec = WAVECAT64CH_OpenDevice(&handle);
        if (ec == WAVECAT64CH_Success) {
            log_msg("Device opened successfully on attempt %d! Handle=%d", attempt, handle);
            g_device_open = 1;
            break;
        }
        log_msg("  Failed with code %d, retrying...", (int)ec);
        sleep(1);
    }
    
    if (!g_device_open) {
        log_msg("FATAL: Failed to open device after 10 attempts");
        log_msg("Check hardware connection and USB permissions");
        return 1;
    }
    
    // Reset and set defaults
    log_msg("Resetting device...");
    WAVECAT64CH_ErrCode ec = WAVECAT64CH_ResetDevice();
    if (ec != WAVECAT64CH_Success) {
        log_msg("WARNING: ResetDevice returned %d", (int)ec);
    }
    
    log_msg("Setting default parameters...");
    ec = WAVECAT64CH_SetDefaultParameters();
    if (ec != WAVECAT64CH_Success) {
        log_msg("WARNING: SetDefaultParameters returned %d", (int)ec);
    }
    
    log_msg("");
    log_msg("===== DEVICE IS OPEN AND READY =====");
    log_msg("You can now start MIDAS frontend");
    log_msg("Frontend will use the already-open device");
    log_msg("This keeper will stay running until you press Ctrl+C");
    log_msg("");
    
    // Just sleep forever, keeping device open
    while (!g_shutdown_requested) {
        sleep(5);
        // Optionally send periodic log messages
        static int counter = 0;
        counter++;
        if (counter % 12 == 0) { // Every minute
            log_msg("Device keeper alive (device still open, handle=%d)", handle);
        }
    }
    
    log_msg("Closing device...");
    ec = WAVECAT64CH_CloseDevice();
    if (ec != WAVECAT64CH_Success) {
        log_msg("WARNING: CloseDevice returned %d", (int)ec);
    }
    
    log_msg("Device keeper exited");
    return 0;
}
