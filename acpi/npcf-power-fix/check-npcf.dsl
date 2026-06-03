/*
 * Intel ACPI Component Architecture
 * AML/ASL+ Disassembler version 20260408 (64-bit version)
 * Copyright (c) 2000 - 2026 Intel Corporation
 * 
 * Disassembling to symbolic ASL+ operators
 *
 * Disassembly of /home/brad/check-npcf.aml
 *
 * Original Table Header:
 *     Signature        "SSDT"
 *     Length           0x00000126 (294)
 *     Revision         0x02
 *     Checksum         0xA0
 *     OEM ID           "BRAD  "
 *     OEM Table ID     "NPCFIX  "
 *     OEM Revision     0x00000006 (6)
 *     Compiler ID      "INTL"
 *     Compiler Version 0x20260408 (539362312)
 */
DefinitionBlock ("", "SSDT", 2, "BRAD  ", "NPCFIX  ", 0x00000006)
{
    External (_SB_.NPCF, DeviceObj)
    External (_SB_.NPCF.ACBT, IntObj)
    External (_SB_.NPCF.AMAT, IntObj)
    External (_SB_.NPCF.AMIT, IntObj)
    External (_SB_.NPCF.ATPP, IntObj)
    External (_SB_.NPCF.DBAC, IntObj)
    External (_SB_.NPCF.DBDC, IntObj)
    External (_SB_.NPCF.DCBT, IntObj)
    External (_SB_.NPCF.DTPP, IntObj)
    External (_SB_.NPCF.NVWM, IntObj)

    Scope (\_SB.NPCF)
    {
        Method (_INI, 0, NotSerialized)  // _INI: Initialize
        {
            AMAT = 0x7530
            ACBT = 0x1D4C
            ATPP = 0x7D00
            DBAC = One
            DBDC = Zero
            NVWM = One
            DCBT = 0x1388
            DTPP = 0x1388
        }
    }
}

