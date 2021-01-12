/*
 * nvgldemo_win_surfaceflinger.h
 *
 * Copyright (c) 2013, NVIDIA CORPORATION. All rights reserved.
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

// Exposes Android display system objects created by nvgldemo to applications
//   which demonstrate Surface-flinger-specific features.

#ifndef __NVGLDEMO_WIN_FLINGER_H
#define __NVGLDEMO_WIN_FLINGER_H

#include <EGL/egl.h>
#include <utils/Errors.h>
#include <ui/PixelFormat.h>
#include <gui/ISurfaceComposer.h>
#include <gui/Surface.h>
#include <gui/SurfaceComposerClient.h>
#include <android/native_window.h>

// Platform-specific state info
struct NvGlDemoPlatformState
{
    EGLDisplay                mDisplay;
    android::sp<ANativeWindow>         mWindow;
    android::sp<android::SurfaceComposerClient> mComposerClient;
    android::sp<android::SurfaceControl>        mSurfaceControl;
    int                       mMouseInputFd;
};

#endif // __NVGLDEMO_WIN_FLINGER_H
