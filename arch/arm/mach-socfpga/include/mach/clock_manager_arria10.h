/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Copyright (C) 2016-2017 Intel Corporation
 */

#ifndef CLOCK_MANAGER_ARRIA10
#define CLOCK_MANAGER_ARRIA10

#ifndef __ASSEMBLY__

#include <linux/bitops.h>

/* Clock manager group */
#define CLKMGR_A10_CTRL				0x00
#define CLKMGR_A10_INTR				0x04
#define CLKMGR_A10_STAT				0x1c
/* MainPLL group */
#define CLKMGR_A10_MAINPLL_VCO0			0x40
#define CLKMGR_A10_MAINPLL_VCO1			0x44
#define CLKMGR_A10_MAINPLL_EN			0x48
#define CLKMGR_A10_MAINPLL_ENS			0x4c
#define CLKMGR_A10_MAINPLL_ENR			0x50
#define CLKMGR_A10_MAINPLL_BYPASS		0x54
#define CLKMGR_A10_MAINPLL_BYPASSS		0x58
#define CLKMGR_A10_MAINPLL_BYPASSR		0x5c
#define CLKMGR_A10_MAINPLL_MPUCLK		0x60
#define CLKMGR_A10_MAINPLL_NOCCLK		0x64
#define CLKMGR_A10_MAINPLL_CNTR2CLK		0x68
#define CLKMGR_A10_MAINPLL_CNTR3CLK		0x6c
#define CLKMGR_A10_MAINPLL_CNTR4CLK		0x70
#define CLKMGR_A10_MAINPLL_CNTR5CLK		0x74
#define CLKMGR_A10_MAINPLL_CNTR6CLK		0x78
#define CLKMGR_A10_MAINPLL_CNTR7CLK		0x7c
#define CLKMGR_A10_MAINPLL_CNTR8CLK		0x80
#define CLKMGR_A10_MAINPLL_CNTR9CLK		0x84
#define CLKMGR_A10_MAINPLL_CNTR15CLK		0x9c
#define CLKMGR_A10_MAINPLL_NOCDIV		0xa8
/* Peripheral PLL group */
#define CLKMGR_A10_PERPLL_VCO0			0xc0
#define CLKMGR_A10_PERPLL_VCO1			0xc4
#define CLKMGR_A10_PERPLL_EN			0xc8
#define CLKMGR_A10_PERPLL_ENS			0xcc
#define CLKMGR_A10_PERPLL_ENR			0xd0
#define CLKMGR_A10_PERPLL_BYPASS		0xd4
#define CLKMGR_A10_PERPLL_BYPASSS		0xd8
#define CLKMGR_A10_PERPLL_BYPASSR		0xdc
#define CLKMGR_A10_PERPLL_CNTR2CLK		0xe8
#define CLKMGR_A10_PERPLL_CNTR3CLK		0xec
#define CLKMGR_A10_PERPLL_CNTR4CLK		0xf0
#define CLKMGR_A10_PERPLL_CNTR5CLK		0xf4
#define CLKMGR_A10_PERPLL_CNTR6CLK		0xf8
#define CLKMGR_A10_PERPLL_CNTR7CLK		0xfc
#define CLKMGR_A10_PERPLL_CNTR8CLK		0x100
#define CLKMGR_A10_PERPLL_CNTR9CLK		0x104
#define CLKMGR_A10_PERPLL_EMACCTL		0x128
#define CLKMGR_A10_PERPLL_GPIOFIV		0x12c
/* Altera group */
#define CLKMGR_A10_ALTR_MPUCLK			0x140
#define CLKMGR_A10_ALTR_NOCCLK			0x144

#define CLKMGR_STAT				CLKMGR_A10_STAT
#define CLKMGR_INTER				CLKMGR_A10_INTER
#define CLKMGR_PERPLL_EN			CLKMGR_A10_PERPLL_EN

#ifdef CONFIG_XPL_BUILD
int cm_basic_init(const void *blob);
#endif

#include <linux/bitops.h>
unsigned int cm_get_l4_sp_clk_hz(void);

#endif /* __ASSEMBLY__ */

#define LOCKED_MASK	(CLKMGR_CLKMGR_STAT_MAINPLLLOCKED_SET_MSK | \
			 CLKMGR_CLKMGR_STAT_PERPLLLOCKED_SET_MSK)

/* value */
#define CLKMGR_MAINPLL_BYPASS_RESET			0x0000003f
#define CLKMGR_PERPLL_BYPASS_RESET			0x000000ff
#define CLKMGR_MAINPLL_VCO0_RESET			0x00010053
#define CLKMGR_MAINPLL_VCO1_RESET			0x00010001
#define CLKMGR_PERPLL_VCO0_RESET			0x00010053
#define CLKMGR_PERPLL_VCO1_RESET			0x00010001
#define CLKMGR_MAINPLL_VCO0_PSRC_EOSC			0x0
#define CLKMGR_MAINPLL_VCO0_PSRC_E_INTOSC		0x1
#define CLKMGR_MAINPLL_VCO0_PSRC_F2S			0x2
#define CLKMGR_PERPLL_VCO0_PSRC_EOSC			0x0
#define CLKMGR_PERPLL_VCO0_PSRC_E_INTOSC		0x1
#define CLKMGR_PERPLL_VCO0_PSRC_F2S			0x2
#define CLKMGR_PERPLL_VCO0_PSRC_MAIN			0x3

/* mask */
#define CLKMGR_MAINPLL_EN_S2FUSER0CLKEN_SET_MSK		BIT(6)
#define CLKMGR_MAINPLL_EN_HMCPLLREFCLKEN_SET_MSK	BIT(7)
#define CLKMGR_CLKMGR_STAT_MAINPLLLOCKED_SET_MSK	BIT(8)
#define CLKMGR_CLKMGR_STAT_PERPLLLOCKED_SET_MSK		BIT(9)
#define CLKMGR_CLKMGR_STAT_BOOTCLKSRC_SET_MSK		BIT(17)
#define CLKMGR_MAINPLL_VCO0_BGPWRDN_SET_MSK		BIT(0)
#define CLKMGR_MAINPLL_VCO0_PWRDN_SET_MSK		BIT(1)
#define CLKMGR_MAINPLL_VCO0_EN_SET_MSK			BIT(2)
#define CLKMGR_MAINPLL_VCO0_OUTRSTALL_SET_MSK		BIT(3)
#define CLKMGR_MAINPLL_VCO0_REGEXTSEL_SET_MSK		BIT(4)
#define CLKMGR_PERPLL_VCO0_BGPWRDN_SET_MSK		BIT(0)
#define CLKMGR_PERPLL_VCO0_PWRDN_SET_MSK		BIT(1)
#define CLKMGR_PERPLL_VCO0_EN_SET_MSK			BIT(2)
#define CLKMGR_PERPLL_VCO0_OUTRSTALL_SET_MSK		BIT(3)
#define CLKMGR_PERPLL_VCO0_REGEXTSEL_SET_MSK		BIT(4)
#define CLKMGR_CLKMGR_INTR_MAINPLLACHIEVED_SET_MSK	BIT(0)
#define CLKMGR_CLKMGR_INTR_PERPLLACHIEVED_SET_MSK	BIT(1)
#define CLKMGR_CLKMGR_INTR_MAINPLLLOST_SET_MSK		BIT(2)
#define CLKMGR_CLKMGR_INTR_PERPLLLOST_SET_MSK		BIT(3)
#define CLKMGR_CLKMGR_INTR_MAINPLLRFSLIP_SET_MSK	BIT(8)
#define CLKMGR_CLKMGR_INTR_PERPLLRFSLIP_SET_MSK		BIT(9)
#define CLKMGR_CLKMGR_INTR_MAINPLLFBSLIP_SET_MSK	BIT(10)
#define CLKMGR_CLKMGR_INTR_PERPLLFBSLIP_SET_MSK		BIT(11)
#define CLKMGR_CLKMGR_CTL_BOOTMOD_SET_MSK		BIT(0)
#define CLKMGR_CLKMGR_CTL_BOOTCLK_INTOSC_SET_MSK	0x00000300
#define CLKMGR_PERPLL_EN_RESET				0x00000f7f
#define CLKMGR_PERPLLGRP_EN_SDMMCCLK_MASK		BIT(5)
#define CLKMGR_MAINPLL_VCO0_PSRC_MSK			0x00000003
#define CLKMGR_MAINPLL_VCO1_NUMER_MSK			0x00001fff
#define CLKMGR_MAINPLL_VCO1_DENOM_MSK			0x0000003f
#define CLKMGR_MAINPLL_CNTRCLK_MSK			0x000003ff
#define CLKMGR_PERPLL_VCO0_PSRC_MSK			0x00000003
#define CLKMGR_PERPLL_VCO1_NUMER_MSK			0x00001fff
#define CLKMGR_PERPLL_VCO1_DENOM_MSK			0x0000003f
#define CLKMGR_PERPLL_CNTRCLK_MSK			0x000003ff
#define CLKMGR_MAINPLL_MPUCLK_SRC_MSK			0x00000007
#define CLKMGR_MAINPLL_MPUCLK_CNT_MSK			0x000003ff
#define CLKMGR_MAINPLL_MPUCLK_SRC_MAIN			0
#define CLKMGR_MAINPLL_MPUCLK_SRC_PERI			1
#define CLKMGR_MAINPLL_MPUCLK_SRC_OSC1			2
#define CLKMGR_MAINPLL_MPUCLK_SRC_INTOSC		3
#define CLKMGR_MAINPLL_MPUCLK_SRC_FPGA			4
#define CLKMGR_MAINPLL_NOCDIV_MSK			0x00000003
#define CLKMGR_MAINPLL_NOCCLK_CNT_MSK			0x000003ff
#define CLKMGR_MAINPLL_NOCCLK_SRC_MSK			0x00000007
#define CLKMGR_MAINPLL_NOCCLK_SRC_MAIN			0
#define CLKMGR_MAINPLL_NOCCLK_SRC_PERI			1
#define CLKMGR_MAINPLL_NOCCLK_SRC_OSC1			2
#define CLKMGR_MAINPLL_NOCCLK_SRC_INTOSC		3
#define CLKMGR_MAINPLL_NOCCLK_SRC_FPGA			4

#define CLKMGR_PERPLLGRP_SRC_MSK			0x00000007
#define CLKMGR_PERPLLGRP_SRC_MAIN			0
#define CLKMGR_PERPLLGRP_SRC_PERI			1
#define CLKMGR_PERPLLGRP_SRC_OSC1			2
#define CLKMGR_PERPLLGRP_SRC_INTOSC			3
#define CLKMGR_PERPLLGRP_SRC_FPGA			4

/* bit shifting macro */
#define CLKMGR_MAINPLL_VCO0_PSRC_LSB		8
#define CLKMGR_PERPLL_VCO0_PSRC_LSB		8
#define CLKMGR_MAINPLL_VCO1_DENOM_LSB		16
#define CLKMGR_PERPLL_VCO1_DENOM_LSB		16
#define CLKMGR_MAINPLL_NOCCLK_PERICNT_LSB	16
#define CLKMGR_MAINPLL_NOCCLK_SRC_LSB		16
#define CLKMGR_MAINPLL_NOCDIV_L4MAINCLK_LSB	0
#define CLKMGR_MAINPLL_NOCDIV_L4MPCLK_LSB	8
#define CLKMGR_MAINPLL_NOCDIV_L4SPCLK_LSB	16
#define CLKMGR_MAINPLL_NOCDIV_CSATCLK_LSB	24
#define CLKMGR_MAINPLL_NOCDIV_CSTRACECLK_LSB	26
#define CLKMGR_MAINPLL_NOCDIV_CSPDBGCLK_LSB	28
#define CLKMGR_MAINPLL_MPUCLK_SRC_LSB		16
#define CLKMGR_MAINPLL_MPUCLK_PERICNT_LSB	16
#define CLKMGR_MAINPLL_NOCCLK_SRC_LSB		16
#define CLKMGR_MAINPLL_CNTR7CLK_SRC_LSB		16
#define CLKMGR_MAINPLL_CNTR9CLK_SRC_LSB		16
#define CLKMGR_PERPLL_CNTR2CLK_SRC_LSB		16
#define CLKMGR_PERPLL_CNTR3CLK_SRC_LSB		16
#define CLKMGR_PERPLL_CNTR4CLK_SRC_LSB		16
#define CLKMGR_PERPLL_CNTR5CLK_SRC_LSB		16
#define CLKMGR_PERPLL_CNTR6CLK_SRC_LSB		16
#define CLKMGR_PERPLL_CNTR8CLK_SRC_LSB		16
#define CLKMGR_PERPLL_EMACCTL_EMAC0SEL_LSB	26
#define CLKMGR_PERPLL_EMACCTL_EMAC1SEL_LSB	27
#define CLKMGR_PERPLL_EMACCTL_EMAC2SEL_LSB	28

/* PLL ramping work around */
#define CLKMGR_PLL_RAMP_MPUCLK_THRESHOLD_HZ	900000000
#define CLKMGR_PLL_RAMP_NOCCLK_THRESHOLD_HZ	300000000
#define CLKMGR_PLL_RAMP_MPUCLK_INCREMENT_HZ	100000000
#define CLKMGR_PLL_RAMP_NOCCLK_INCREMENT_HZ	33000000

#define CLKMGR_STAT_BUSY			BIT(0)

#endif /* CLOCK_MANAGER_ARRIA10 */
