/*
 * Intel ACPI Component Architecture
 * AML/ASL+ Disassembler version 20260408 (64-bit version)
 * Copyright (c) 2000 - 2026 Intel Corporation
 * 
 * Disassembling to symbolic ASL+ operators
 *
 * Source for npcf-v8.aml (80W GPU TGP — current fix)
 *
 * Table Header:
 *     Signature        "SSDT"
 *     Length           0x000002C7 (711)
 *     Revision         0x02
 *     OEM ID           "BRAD  "
 *     OEM Table ID     "NPCFV8  "
 *     OEM Revision     0x00000008 (8)
 *     Compiler ID      "INTL"
 *     Compiler Version 0x20260408 (539362312)
 */
DefinitionBlock ("", "SSDT", 2, "BRAD  ", "NPCFV8  ", 0x00000008)
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
    External (_SB_.NPCF.NPCF, MethodObj)    // 4 Arguments
    External (_SB_.NPCF.NVWM, IntObj)
    External (_SB_.PC00.PEG0.PEGP.NPCS, IntObj)

    Scope (\_SB.NPCF)
    {
        Method (_INI, 0, NotSerialized)  // _INI: Initialize
        {
            ACBT = 0x0280
            DCBT = 0x0190
            AMAT = 0x0960
            ATPP = 0x0A00
            DTPP = 0x0190
            DBAC = One
            DBDC = Zero
            NVWM = One
            AMIT = Zero
        }

        Method (_DSM, 4, Serialized)  // _DSM: Device-Specific Method
        {
            If ((Arg0 == ToUUID ("36b49710-2483-11e7-9598-0800200c9a66") /* Unknown UUID */))
            {
                If ((\_SB.PC00.PEG0.PEGP.NPCS != Zero))
                {
                    If ((ToInteger (Arg1) == 0x0200))
                    {
                        If ((ToInteger (Arg2) == 0x02))
                        {
                            Return (PWBG (Arg3))
                        }
                    }

                    Return (\_SB.NPCF.NPCF (Arg0, Arg1, Arg2, Arg3))
                }
            }

            Return (Ones)
        }

        Method (PWBG, 1, Serialized)
        {
            Name (PBUF, Buffer (0x31)
            {
                 0x00                                             // .
            })
            CreateByteField (PBUF, Zero, BTYP)
            CreateByteField (PBUF, One, BHDZ)
            CreateByteField (PBUF, 0x02, BGSZ)
            CreateByteField (PBUF, 0x03, BCTZ)
            CreateByteField (PBUF, 0x04, BNCE)
            CreateWordField (PBUF, 0x05, BTGA)
            CreateWordField (PBUF, 0x07, BTGD)
            CreateByteField (PBUF, 0x15, BPC1)
            CreateByteField (PBUF, 0x16, BPC2)
            CreateWordField (PBUF, 0x19, BTPA)
            CreateWordField (PBUF, 0x1B, BTPD)
            CreateWordField (PBUF, 0x1D, BMGA)
            BTYP = 0x23
            BHDZ = 0x05
            BGSZ = 0x10
            BCTZ = 0x1C
            BNCE = One
            CreateField (Arg0, 0x28, 0x02, NIGS)
            If ((ToInteger (NIGS) == Zero))
            {
                BTGA = 0x0280
                BTGD = 0x0190
                BPC1 = Zero
                BPC2 = Zero
                BTPA = 0x0A00
                BTPD = 0x0190
                BMGA = 0x0960
            }

            Return (PBUF) /* \_SB_.NPCF.PWBG.PBUF */
        }
    }
}

