/*
 * cube_frag.glslv
 *
 * Copyright (c) 2009-2013, NVIDIA CORPORATION. All rights reserved.
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

// Fragment shader for rotating textured cube

precision mediump float;    // Default precision
uniform sampler2D texunit;  // Texture unit

varying vec2      texcoord; // Texture coordinate

void main() {

    // If outside the texture, fill in with NVIDIA green
    if ((abs(texcoord.x) > 1.0) || (abs(texcoord.y) > 1.0))
        gl_FragColor = vec4(0.46, 0.73, 0.00, 1.0);

    // Otherwise map from [-1,+1] to [0,1] and get texture value
    else
        gl_FragColor = texture2D(texunit, 0.5*(texcoord+vec2(1,1)));
}
