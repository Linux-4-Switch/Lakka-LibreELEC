/*
 * nvgldemo_win_surfaceflinger.c
 *
 * Copyright (c) 2013-2014, NVIDIA CORPORATION. All rights reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */

//
// This file illustrates how to access the display and create a window for
//   a GL application using Surface-Flinger.
//

#include "nvgldemo.h"
#include "nvgldemo_win_surfaceflinger.h"
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <ui/DisplayInfo.h>

using namespace android;

//
// TODO: Callback handling
//
static NvGlDemoCloseCB   closeCB   = NULL;
static NvGlDemoResizeCB  resizeCB  = NULL;
static NvGlDemoKeyCB     keyCB     = NULL;
static NvGlDemoPointerCB pointerCB = NULL;
static NvGlDemoButtonCB  buttonCB  = NULL;

void NvGlDemoSetCloseCB(NvGlDemoCloseCB cb)     { closeCB   = cb; }
void NvGlDemoSetResizeCB(NvGlDemoResizeCB cb)   { resizeCB  = cb; }
void NvGlDemoSetKeyCB(NvGlDemoKeyCB cb)         { keyCB     = cb; }
void NvGlDemoSetPointerCB(NvGlDemoPointerCB cb) { pointerCB = cb; }
void NvGlDemoSetButtonCB(NvGlDemoButtonCB cb)   { buttonCB  = cb; }

struct MouseState {
    int left, middle, right;
    signed char x, y;
};

//
// Window system startup/shutdown
//

// Initialize access to the display system
int
NvGlDemoDisplayInit(void)
{
    // Allocate a structure for the platform-specific state
    demoState.platform =
        (NvGlDemoPlatformState*)MALLOC(sizeof(NvGlDemoPlatformState));
    if (!demoState.platform) {
        NvGlDemoLog("Could not allocate platform specific storage memory.\n");
        goto fail;
    }
    // Setting default display
    demoState.platform->mDisplay = EGL_DEFAULT_DISPLAY;

    demoState.nativeDisplay =
        (EGLNativeDisplayType)demoState.platform->mDisplay;

    // If display option is specified, but isn't supported, then exit.
    if (demoOptions.displayRate) {
        NvGlDemoLog("Setting display refresh is not supported. Exiting.\n");
        goto fail;
    }

    // But do not fail on the unsupported "displaysize"
    // option (that are also a side effect of the "res" option).
    // We will ignore these here.

    if (demoOptions.displaySize[0]) {
        NvGlDemoLog("Setting display size is not supported. Ignoring.\n");
    }

    demoState.platform->mMouseInputFd = -1;

    return 1;

    fail:
    FREE(demoState.platform);
    demoState.platform = NULL;

    return 0;
}

// Terminate access to the display system
void
NvGlDemoDisplayTerm(void)
{
    if (demoState.platform) {
        demoState.platform->mDisplay = EGL_NO_DISPLAY;

        if (demoState.platform->mMouseInputFd != -1) {
            close(demoState.platform->mMouseInputFd);
        }

        FREE(demoState.platform);
        demoState.platform = NULL;
    }
}

// Create the window
int
NvGlDemoWindowInit(
    int* argc, char** argv,
    const char* appName)
{
    int32_t layer = 0x7FFFFFFF;
    String8 dName(demoOptions.displayName);

    // If not specified, use default window size
    if (!demoOptions.windowSize[0])
        demoOptions.windowSize[0] = NVGLDEMO_DEFAULT_WIDTH;
    if (!demoOptions.windowSize[1])
        demoOptions.windowSize[1] = NVGLDEMO_DEFAULT_HEIGHT;

    demoState.platform->mComposerClient = new SurfaceComposerClient;

#if !PLATFORM_IS_AFTER_P
    sp<IBinder> display(SurfaceComposerClient::getBuiltInDisplay(ISurfaceComposer::eDisplayIdMain));
    DisplayInfo info;
    demoState.platform->mComposerClient->getDisplayInfo(display, &info);

    if (demoOptions.fullScreen) {
        demoOptions.windowSize[0] = info.w;
        demoOptions.windowSize[1] = info.h;
    }
#else
    // TODO: implement for Q. getInternalDisplayToken() looks related.
    if (demoOptions.fullScreen) {
        NvGlDemoLog("Warning: Queyring fullscreen window size is not implemented on android Q.\n");
    }
#endif

    #define FLAG_FULLSCREEN 0x00000400
    int flags = 0;
    if (demoOptions.fullScreen) {
        flags |= FLAG_FULLSCREEN;
    }

    demoState.platform->mSurfaceControl = demoState.platform->mComposerClient->createSurface(
                    dName,
                    demoOptions.windowSize[0], demoOptions.windowSize[1],
                    PIXEL_FORMAT_RGBA_8888, flags);

    if (demoState.platform->mSurfaceControl == NULL ||
        !(demoState.platform->mSurfaceControl->isValid())) {
        NvGlDemoLog("Making Surface Control failed! Exiting.\n");
        goto fail;
    }

    if (demoOptions.displayLayer > 0) {
        layer = demoOptions.displayLayer;
    }

#if defined(PLATFORM_IS_AFTER_O_MR1) && PLATFORM_IS_AFTER_O_MR1
    // scope these statements so that goto fail above doesn't fail the compile
    {
        SurfaceComposerClient::Transaction t;
        if (demoOptions.displayAlpha >= 0.0) {
            t.setAlpha(demoState.platform->mSurfaceControl, demoOptions.displayAlpha);
        }
        t.setLayer(demoState.platform->mSurfaceControl, layer);
        t.show(demoState.platform->mSurfaceControl);
        t.apply();
    }
#else
    SurfaceComposerClient::openGlobalTransaction();
    if (demoOptions.displayAlpha >= 0.0 &&
        demoState.platform->mSurfaceControl->setAlpha(demoOptions.displayAlpha) != NO_ERROR) {
        NvGlDemoLog("Surface Control failed to set alpha! Exiting.\n");
        goto fail;
    }
    if (demoState.platform->mSurfaceControl->setLayer(layer) != NO_ERROR) {
        NvGlDemoLog("Surface Control failed to set layer! Exiting.\n");
        goto fail;
    }
    if (demoState.platform->mSurfaceControl->show() != NO_ERROR) {
        NvGlDemoLog("Surface Control show failed! Exiting.\n");
        goto fail;
    }
    SurfaceComposerClient::closeGlobalTransaction();
#endif

    // Create a native window
    demoState.platform->mWindow = demoState.platform->mSurfaceControl->getSurface();
    if (demoState.platform->mWindow == NULL) {
        NvGlDemoLog("Error creating native window.\n");
        goto fail;
    }
    demoState.nativeWindow = (NativeWindowType)demoState.platform->mWindow.get();

    if (resizeCB) {
        resizeCB(demoOptions.windowSize[0], demoOptions.windowSize[1]);
    }

    //TODO: Set up window properties
    return 1;

    fail:
    NvGlDemoWindowTerm();
    return 0;
}

// Close the window
void
NvGlDemoWindowTerm(void)
{
    if (demoState.platform && demoState.platform->mComposerClient != NULL) {
        demoState.platform->mComposerClient->dispose();
        demoState.platform->mWindow = (sp<ANativeWindow>)0;
        demoState.nativeWindow = (NativeWindowType)0;
    }
}


//
// TODO: Pixmap support
//

EGLNativePixmapType
NvGlDemoPixmapCreate(
    unsigned int width,
    unsigned int height,
    unsigned int depth)
{
    NvGlDemoLog("Flinger pixmap functions not supported\n");
    return (EGLNativePixmapType)0;
}

void
NvGlDemoPixmapDelete(
    EGLNativePixmapType pixmap)
{
    NvGlDemoLog("Flinger pixmap functions not supported\n");
}

void NvGlDemoCheckEvents(void)
{
//TODO: implementation
// read this : http://developer.android.com/reference/android/app/NativeActivity.html
//

    // Persistent mouse data.
    static int mouseX = 0;
    static int mouseY = 0;
    static MouseState oldState = {};

    // Open Mouse
    static bool triedOpeningMouse = false;
    if (!triedOpeningMouse) {
        triedOpeningMouse = true;
        const char *mouseDevicePath = "/dev/input/mice";
        demoState.platform->mMouseInputFd = open(mouseDevicePath, O_RDWR);
        if (demoState.platform->mMouseInputFd) {
            int flags = fcntl(demoState.platform->mMouseInputFd, F_GETFL, 0);
            fcntl(demoState.platform->mMouseInputFd, F_SETFL, flags | O_NONBLOCK);
        } else {
            fprintf(stderr, "ERROR Opening %s\n", mouseDevicePath);
        }
    }

    if (demoState.platform->mMouseInputFd == -1) {
        return;
    }

    int bytes;
    unsigned char data[3];
    for (;;) {
        // Read Mouse
        bytes = read(demoState.platform->mMouseInputFd, data, sizeof(data));

        if (bytes <= 0) {
            break;
        }

        MouseState state;
        state.left = data[0] & 0x1 ? 1 : 0;
        state.right = data[0] & 0x2 ? 1 : 0;
        state.middle = data[0] & 0x4 ? 1 : 0;
        state.x = data[1];
        state.y = data[2];

        if (pointerCB && (state.x != 0 || state.y != 0)) {
            mouseX += state.x;
            mouseY -= state.y;
            mouseX = std::min(std::max(mouseX, 0), demoOptions.windowSize[0] - 1);
            mouseY = std::min(std::max(mouseY, 0), demoOptions.windowSize[1] - 1);
            pointerCB(mouseX, mouseY);
        }

        if (buttonCB && oldState.left != state.left) {
            buttonCB(1, state.left);
        }

        if (buttonCB && oldState.right != state.right) {
            buttonCB(2, state.right);
        }

        if (buttonCB && oldState.middle != state.middle) {
            buttonCB(0, state.middle);
        }

        oldState = state;
    }
}

EGLBoolean NvGlDemoSwapInterval(EGLDisplay dpy, EGLint interval)
{
    return eglSwapInterval(dpy, interval);
}

