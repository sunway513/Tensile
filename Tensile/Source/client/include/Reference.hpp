/**
 * MIT License
 *
 * Copyright (C) 2019 Advanced Micro Devices, Inc. All rights reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell cop-
 * ies of the Software, and to permit persons to whom the Software is furnished
 * to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IM-
 * PLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNE-
 * CTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#pragma once

#include <Tensile/ContractionProblem.hpp>

#include <Tensile/DataTypes.hpp>

namespace Tensile
{
    namespace Client
    {
        template <typename T>
        inline bool AlmostEqual(T a, T b);

        template<>
        inline bool AlmostEqual(Half a, Half b)
        {
            Half absA = (a > 0) ? a : -a;
            Half absB = (b > 0) ? b : -b;
            Half absDiff = (a-b > 0) ? a-b : b-a;
            return absDiff/(absA+absB+1) < 0.01;
        }

        template<>
        inline bool AlmostEqual(BFloat16 a, BFloat16 b)
        {
            BFloat16 absA = (a > static_cast<BFloat16>(0.0f)) ? a : static_cast<BFloat16>(0.0f) - a;
            BFloat16 absB = (b > static_cast<BFloat16>(0.0f)) ? b : static_cast<BFloat16>(0.0f) - b;
            BFloat16 absDiff = (a-b > static_cast<BFloat16>(0.0f)) ? a-b : b-a;
            return absDiff/(absA+absB+static_cast<BFloat16>(1.0f)) < static_cast<BFloat16>(0.1f);
        }

        template<>
        inline bool AlmostEqual(float a, float b)
        {
            return std::fabs(a - b)/(std::fabs(a)+std::fabs(b)+1) < 0.0001; // 7 digits of precision - 2
        }

        template<>
        inline bool AlmostEqual(double a, double b)
        {
            return std::fabs(a - b) / ( std::fabs(a) + std::fabs(b)+1 ) < 0.000000000001; // 15 digits of precision - 2
        }
        template<>
        inline bool AlmostEqual(int a, int b)
        {
            return a == b;
        }
        template<>
        inline bool AlmostEqual(unsigned int a, unsigned int b)
        {
            return a == b;
        }
        template<>
        inline bool AlmostEqual( std::complex<float> a, std::complex<float> b)
        {
            return AlmostEqual(a.real(), b.real()) && AlmostEqual(a.imag(), b.imag());
        }

        template<>
        inline bool AlmostEqual( std::complex<double> a, std::complex<double> b)
        {
            return AlmostEqual(a.real(), b.real()) && AlmostEqual(a.imag(), b.imag());
        }

        template <typename Inputs, typename Accumulator = typename Inputs::DType>
        struct ReferenceSolution
        {
            static void SolveCPU(ContractionProblem const& contraction, Inputs const& inputs, size_t validationStride = 1);
        };

        void SolveCPU(ContractionProblem const& contraction, ContractionInputs const& inputs, size_t validationStride = 1);
    }
}

