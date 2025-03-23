/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Copyright (c) 2010-2012, NVIDIA CORPORATION.  All rights reserved.
 *
 * Copyright (c) 2021, Open Surface RT
 */

#ifndef __CONFIG_H
#define __CONFIG_H

#include "tegra30-common.h"

/* High-level configuration options */
#define CFG_TEGRA_BOARD_STRING		"Microsoft Surface RT"

/* Board-specific serial config */
#define CFG_SYS_NS16550_COM1		NV_PA_APB_UARTA_BASE

#include "tegra-common-post.h"

#endif /* __CONFIG_H */
