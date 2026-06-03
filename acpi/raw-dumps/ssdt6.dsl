/*
 * Intel ACPI Component Architecture
 * AML/ASL+ Disassembler version 20240322 (64-bit version)
 * Copyright (c) 2000 - 2023 Intel Corporation
 * 
 * Disassembling to symbolic ASL+ operators
 *
 * Disassembly of ssdt6.dat
 *
 * Original Table Header:
 *     Signature        "SSDT"
 *     Length           0x00002446 (9286)
 *     Revision         0x01
 *     Checksum         0xBE
 *     OEM ID           "ACRSYS"
 *     OEM Table ID     "ACRPRDCT"
 *     OEM Revision     0x00001000 (4096)
 *     Compiler ID      "1025"
 *     Compiler Version 0x00040000 (262144)
 */
DefinitionBlock ("", "SSDT", 1, "ACRSYS", "ACRPRDCT", 0x00001000)
{
    External (_SB_.CDSB, UnknownObj)
    External (_SB_.CPUI, UnknownObj)
    External (_SB_.GGIV, MethodObj)    // 1 Arguments
    External (_SB_.PC00, DeviceObj)
    External (_SB_.PC00.LPCB.EC0_._QC8, MethodObj)    // 0 Arguments
    External (_SB_.PC00.LPCB.EC0_.CTMP, UnknownObj)
    External (_SB_.PC00.LPCB.EC0_.DP1H, UnknownObj)
    External (_SB_.PC00.LPCB.EC0_.DP1L, UnknownObj)
    External (_SB_.PC00.LPCB.EC0_.DP2H, UnknownObj)
    External (_SB_.PC00.LPCB.EC0_.DP2L, UnknownObj)
    External (_SB_.PC00.LPCB.EC0_.EC6E, MethodObj)    // 1 Arguments
    External (_SB_.PC00.LPCB.EC0_.ECDW, MethodObj)    // 1 Arguments
    External (_SB_.PC00.LPCB.EC0_.ETP1, UnknownObj)
    External (_SB_.PC00.LPCB.EC0_.GTMP, UnknownObj)
    External (_SB_.PC00.LPCB.EC0_.VGAF, UnknownObj)
    External (_SB_.PC00.PEG0, DeviceObj)
    External (_SB_.PC00.PEG0.DL23, MethodObj)    // 0 Arguments
    External (_SB_.PC00.PEG0.L23D, MethodObj)    // 0 Arguments
    External (_SB_.PC00.PEG0.PEGP, DeviceObj)
    External (_SB_.PC00.PEG0.PXP_._OFF, MethodObj)    // 0 Arguments
    External (_SB_.PC00.PEG0.PXP_._ON_, MethodObj)    // 0 Arguments
    External (_SB_.PC00.PEG0.RSTG, IntObj)
    External (_SB_.PR00, DeviceObj)
    External (_SB_.PR01, DeviceObj)
    External (_SB_.PR02, DeviceObj)
    External (_SB_.PR03, DeviceObj)
    External (_SB_.PR04, DeviceObj)
    External (_SB_.PR05, DeviceObj)
    External (_SB_.PR06, DeviceObj)
    External (_SB_.PR07, DeviceObj)
    External (_SB_.PR08, DeviceObj)
    External (_SB_.PR09, DeviceObj)
    External (_SB_.PR10, DeviceObj)
    External (_SB_.PR11, DeviceObj)
    External (_SB_.PR12, DeviceObj)
    External (_SB_.PR13, DeviceObj)
    External (_SB_.PR14, DeviceObj)
    External (_SB_.PR15, DeviceObj)
    External (_SB_.PR16, DeviceObj)
    External (_SB_.PR17, DeviceObj)
    External (_SB_.PR18, DeviceObj)
    External (_SB_.PR19, DeviceObj)
    External (_SB_.PR20, DeviceObj)
    External (_SB_.PR21, DeviceObj)
    External (_SB_.PR22, DeviceObj)
    External (_SB_.PR23, DeviceObj)
    External (_SB_.VRDY, UnknownObj)
    External (_SB_.VSID, UnknownObj)
    External (HRA0, UnknownObj)
    External (HRE0, UnknownObj)
    External (HRG0, UnknownObj)
    External (PIN_.OFF_, MethodObj)    // 1 Arguments
    External (PIN_.ON__, MethodObj)    // 1 Arguments
    External (SGGP, UnknownObj)
    External (TCNT, FieldUnitObj)

    Scope (\_SB.PC00)
    {
        OperationRegion (HGOP, SystemMemory, 0x319DDF18, 0x00000012)
        Field (HGOP, AnyAcc, Lock, Preserve)
        {
            DGDA,   32, 
            DGBA,   32, 
            OPTF,   8, 
            NVGE,   8, 
            DSSV,   32, 
            DISM,   8, 
            DISG,   8, 
            DISS,   8, 
            HGST,   8
        }
    }

    Scope (\_SB.PC00.PEG0.PEGP)
    {
        OperationRegion (VBOR, SystemMemory, 0x34892018, 0x00040004)
        Field (VBOR, DWordAcc, Lock, Preserve)
        {
            RVBS,   32, 
            VBS1,   262144, 
            VBS2,   262144, 
            VBS3,   262144, 
            VBS4,   262144, 
            VBS5,   262144, 
            VBS6,   262144, 
            VBS7,   262144, 
            VBS8,   262144
        }
    }

    Scope (\_SB.PC00.PEG0.PEGP)
    {
        OperationRegion (NOPR, SystemMemory, 0x3488F018, 0x00002027)
        Field (NOPR, AnyAcc, Lock, Preserve)
        {
            DHPS,   8, 
            DPCS,   8, 
            GPSS,   8, 
            VENS,   8, 
            NBCS,   8, 
            GC6S,   8, 
            NVSR,   8, 
            NPCS,   8, 
            SLVS,   8, 
            PBCM,   8, 
            EXMD,   8, 
            MXBS,   32, 
            MXMB,   32768, 
            SMXS,   32, 
            SMXB,   32768, 
            FBEN,   32, 
            ENVT,   32, 
            PWGD,   32, 
            DMMP,   32, 
            DLRP,   32
        }
    }

    Scope (\_SB.PC00.PEG0)
    {
        OperationRegion (RPCX, SystemMemory, \_SB.PC00.DGBA, 0x1000)
        Field (RPCX, DWordAcc, NoLock, Preserve)
        {
            Offset (0x04), 
            CMDR,   8, 
            Offset (0x19), 
            PRBN,   8, 
            Offset (0x4A), 
            CEDR,   1, 
            Offset (0x69), 
                ,   2, 
            LREN,   1, 
            Offset (0xA4), 
            D0ST,   2
        }

        Method (GSTA, 0, NotSerialized)
        {
            If ((\_SB.GGIV (\_SB.PC00.PEG0.PEGP.PWGD) == Zero))
            {
                Return (Zero)
            }
            Else
            {
                Return (One)
            }
        }
    }

    Scope (\_SB.PC00.PEG0.PEGP)
    {
        Name (LTRE, Zero)
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            Return (0x0F)
        }

        OperationRegion (PCIM, SystemMemory, \_SB.PC00.DGDA, 0x1000)
        Field (PCIM, DWordAcc, NoLock, Preserve)
        {
            NVID,   16, 
            NDID,   16, 
            CMDR,   8, 
            VGAR,   2008, 
            Offset (0x48B), 
                ,   1, 
            HDAE,   1
        }

        OperationRegion (DGPU, SystemMemory, \_SB.PC00.DGDA, 0x0100)
        Field (DGPU, DWordAcc, NoLock, Preserve)
        {
            Offset (0x40), 
            SSSV,   32
        }

        Method (_REG, 2, NotSerialized)  // _REG: Region Availability
        {
            If (((Arg0 == 0x02) && (Arg1 == One)))
            {
                \_SB.VRDY = 0xAA
            }

            If (((Arg0 == 0x02) && (Arg1 == Zero)))
            {
                \_SB.VRDY = Zero
            }

            \_SB.PC00.LPCB.EC0._QC8 ()
        }

        Method (_DSM, 4, Serialized)  // _DSM: Device-Specific Method
        {
            If ((Arg0 == ToUUID ("a486d8f8-0bda-471b-a72b-6042a6b5bee0") /* Unknown UUID */))
            {
                Return (\_SB.PC00.PEG0.PEGP.NVOP (Arg0, Arg1, Arg2, Arg3))
            }

            If ((Arg0 == ToUUID ("a3132d01-8cda-49ba-a52e-bc9d46df6b81") /* Unknown UUID */))
            {
                If ((\_SB.PC00.PEG0.PEGP.GPSS != Zero))
                {
                    Return (\_SB.PC00.PEG0.PEGP.GPS (Arg0, Arg1, Arg2, Arg3))
                }
            }

            If ((Arg0 == ToUUID ("cbeca351-067b-4924-9cbd-b46b00b86f34") /* Unknown UUID */))
            {
                If ((\_SB.PC00.PEG0.PEGP.GC6S != Zero))
                {
                    Return (\_SB.PC00.PEG0.PEGP.NVJT (Arg0, Arg1, Arg2, Arg3))
                }
            }

            If ((Arg0 == ToUUID ("d4a50b75-65c7-46f7-bfb7-41514cea0244") /* Unknown UUID */))
            {
                If ((\_SB.PC00.PEG0.PEGP.NBCS != Zero))
                {
                    Return (\_SB.PC00.PEG0.PEGP.NBCI (Arg0, Arg1, Arg2, Arg3))
                }
            }

            Return (0x80000001)
        }
    }

    Scope (\_SB.PC00.PEG0.PEGP)
    {
        Name (VGAB, Buffer (0xFB)
        {
             0x00                                             // .
        })
        Method (_PS0, 0, NotSerialized)  // _PS0: Power State 0
        {
            If ((DGPS != Zero))
            {
                \_SB.PC00.PEG0.PXP._ON ()
                If ((GPRF != One))
                {
                    VGAR = VGAB /* \_SB_.PC00.PEG0.PEGP.VGAB */
                }

                DGPS = Zero
            }
        }

        Method (_PS3, 0, NotSerialized)  // _PS3: Power State 3
        {
            If ((OMPR == 0x03))
            {
                If ((GPRF != One))
                {
                    VGAB = VGAR /* \_SB_.PC00.PEG0.PEGP.VGAR */
                }

                \_SB.PC00.PEG0.PXP._OFF ()
                DGPS = One
                OMPR = 0x02
            }
        }

        Name (DGPS, Zero)
        Name (OMPR, 0x02)
        Name (GPRF, Zero)
        Name (DPST, One)
        Method (NVOP, 4, Serialized)
        {
            Debug = "------- NV OPTIMUS DSM --------"
            If ((Arg1 != 0x0100))
            {
                Return (0x80000001)
            }

            Switch (ToInteger (Arg2))
            {
                Case (Zero)
                {
                    Debug = "   NVOP fun0 NVOP_FUNC_SUPPORT"
                    Return (Buffer (0x04)
                    {
                         0x01, 0x00, 0x00, 0x0C                           // ....
                    })
                }
                Case (0x1A)
                {
                    Debug = "   NVOP fun26 NVOP_FUNC_OPTIMUSCAPS"
                    CreateField (Arg3, Zero, One, FLCH)
                    CreateField (Arg3, One, One, DVSR)
                    CreateField (Arg3, 0x02, One, DVSC)
                    CreateField (Arg3, 0x18, 0x02, OPCE)
                    If ((ToInteger (FLCH) && (ToInteger (OPCE) != OMPR)))
                    {
                        OMPR = ToInteger (OPCE)
                    }

                    Local0 = Buffer (0x04)
                        {
                             0x00, 0x00, 0x00, 0x00                           // ....
                        }
                    CreateField (Local0, Zero, One, OPEN)
                    CreateField (Local0, 0x03, 0x02, CGCS)
                    CreateField (Local0, 0x06, One, SHPC)
                    CreateField (Local0, 0x08, One, SNSR)
                    CreateField (Local0, 0x18, 0x03, DGPC)
                    CreateField (Local0, 0x1B, 0x02, OHAC)
                    OPEN = One
                    SHPC = One
                    DGPC = One
                    OHAC = 0x03
                    If (ToInteger (DVSC))
                    {
                        If (ToInteger (DVSR))
                        {
                            GPRF = One
                        }
                        Else
                        {
                            GPRF = Zero
                        }
                    }

                    SNSR = GPRF /* \_SB_.PC00.PEG0.PEGP.GPRF */
                    If ((DGPS == Zero))
                    {
                        CGCS = 0x03
                    }
                    Else
                    {
                        CGCS = Zero
                    }

                    Return (Local0)
                }
                Case (0x1B)
                {
                    Debug = "   NVOP fun27 NVOP_FUNC_OPTIMUSFLAGS"
                    CreateField (Arg3, Zero, One, OACC)
                    CreateField (Arg3, One, One, UOAC)
                    CreateField (Arg3, 0x02, 0x08, OPDA)
                    CreateField (Arg3, 0x0A, One, OPDE)
                    Local1 = Zero
                    Local1 = \_SB.PC00.PEG0.PEGP.HDAE
                    Return (Local1)
                }
                Default
                {
                    Return (0x80000002)
                }

            }
        }
    }

    Scope (\_SB.PC00.PEG0.PEGP)
    {
        Name (NLIM, One)
        Name (PSLS, Zero)
        Name (GPSP, Buffer (0x28){})
        CreateDWordField (GPSP, Zero, RETN)
        CreateDWordField (GPSP, 0x04, VRV1)
        CreateDWordField (GPSP, 0x08, TGPU)
        CreateDWordField (GPSP, 0x0C, PDTS)
        CreateDWordField (GPSP, 0x10, SFAN)
        CreateDWordField (GPSP, 0x14, SKNT)
        CreateDWordField (GPSP, 0x18, CPUE)
        CreateDWordField (GPSP, 0x1C, TMP1)
        CreateDWordField (GPSP, 0x20, TMP2)
        Method (GPS, 4, Serialized)
        {
            Debug = "------- NV GPS DSM --------"
            If ((Arg1 != 0x0200))
            {
                Return (0x80000002)
            }

            Switch (ToInteger (Arg2))
            {
                Case (Zero)
                {
                    Debug = "   GPS fun 0"
                    Return (Buffer (0x08)
                    {
                         0x01, 0x00, 0x0C, 0x00, 0x01, 0x04, 0x00, 0x00   // ........
                    })
                }
                Case (0x12)
                {
                    Debug = "   GPS fun 18"
                }
                Case (0x13)
                {
                    Debug = "   GPS fun 19"
                    CreateDWordField (Arg3, Zero, TEMP)
                    If ((TEMP == Zero))
                    {
                        Return (0x04)
                    }

                    If ((TEMP && 0x04))
                    {
                        Return (0x04)
                    }
                }
                Case (0x20)
                {
                    Debug = "   GPS fun 32"
                    Name (RET1, Zero)
                    CreateBitField (Arg3, 0x02, SPBI)
                    If (NLIM)
                    {
                        RET1 |= One
                    }

                    If (PSLS)
                    {
                        RET1 |= 0x02
                    }

                    Return (RET1) /* \_SB_.PC00.PEG0.PEGP.GPS_.RET1 */
                }
                Case (0x2A)
                {
                    Debug = "   GPS fun 42"
                    CreateField (Arg3, Zero, 0x04, PSH0)
                    CreateBitField (Arg3, 0x08, GPUT)
                    VRV1 = 0x00010000
                    Switch (ToInteger (PSH0))
                    {
                        Case (Zero)
                        {
                            Return (GPSP) /* \_SB_.PC00.PEG0.PEGP.GPSP */
                        }
                        Case (One)
                        {
                            RETN = 0x0100
                            RETN |= ToInteger (PSH0)
                            Return (GPSP) /* \_SB_.PC00.PEG0.PEGP.GPSP */
                        }
                        Case (0x02)
                        {
                            RETN = 0x0102
                            TGPU = 0x57
                            Return (GPSP) /* \_SB_.PC00.PEG0.PEGP.GPSP */
                        }

                    }
                }
                Default
                {
                    Return (0x80000002)
                }

            }

            Return (0x80000002)
        }
    }

    Scope (\_SB.PC00)
    {
        Name (TDGC, Zero)
        Name (DGCX, Zero)
        Name (TGPC, Buffer (0x04)
        {
             0x00                                             // .
        })
        Method (GC6I, 0, Serialized)
        {
            \_SB.PC00.LPCB.EC0.VGAF = Zero
            Debug = "   JT GC6I"
            \_SB.PC00.PEG0.PEGP.LTRE = \_SB.PC00.PEG0.LREN
            \_SB.PC00.PEG0.DL23 ()
            Sleep (0x0A)
            \PIN.ON (\_SB.PC00.PEG0.RSTG)
        }

        Method (GC6O, 0, Serialized)
        {
            Debug = "   JT GC6O"
            \PIN.OFF (\_SB.PC00.PEG0.RSTG)
            \_SB.PC00.PEG0.L23D ()
            \_SB.PC00.PEG0.CMDR |= 0x04
            \_SB.PC00.PEG0.D0ST = Zero
            While ((\_SB.PC00.PEG0.PEGP.NVID != 0x10DE))
            {
                Sleep (One)
            }

            \_SB.PC00.PEG0.LREN = \_SB.PC00.PEG0.PEGP.LTRE
            \_SB.PC00.PEG0.CEDR = One
            \_SB.PC00.LPCB.EC0.VGAF = One
        }
    }

    Scope (\_SB.PC00.PEG0.PEGP)
    {
        Method (NVJT, 4, Serialized)
        {
            Debug = "------- NV JT DSM --------"
            If ((ToInteger (Arg1) < 0x0100))
            {
                Return (0x80000001)
            }

            Switch (ToInteger (Arg2))
            {
                Case (Zero)
                {
                    Debug = "   JT fun0 JT_FUNC_SUPPORT"
                    Return (Buffer (0x04)
                    {
                         0x1B, 0x00, 0x00, 0x00                           // ....
                    })
                }
                Case (One)
                {
                    Debug = "   JT fun1 JT_FUNC_CAPS"
                    Name (JTCA, Buffer (0x04)
                    {
                         0x00                                             // .
                    })
                    CreateField (JTCA, Zero, One, JTEN)
                    CreateField (JTCA, One, 0x02, SREN)
                    CreateField (JTCA, 0x03, 0x02, PLPR)
                    CreateField (JTCA, 0x05, One, SRPR)
                    CreateField (JTCA, 0x06, 0x02, FBPR)
                    CreateField (JTCA, 0x08, 0x02, GUPR)
                    CreateField (JTCA, 0x0A, One, GC6R)
                    CreateField (JTCA, 0x0B, One, PTRH)
                    CreateField (JTCA, 0x0D, One, MHYB)
                    CreateField (JTCA, 0x0E, One, RPCL)
                    CreateField (JTCA, 0x0F, 0x02, GC6V)
                    CreateField (JTCA, 0x11, One, GEIS)
                    CreateField (JTCA, 0x12, One, GSWS)
                    CreateField (JTCA, 0x14, 0x0C, JTRV)
                    JTEN = One
                    GC6R = Zero
                    RPCL = One
                    SREN = One
                    FBPR = Zero
                    MHYB = One
                    GC6V = 0x02
                    JTRV = 0x0200
                    Return (JTCA) /* \_SB_.PC00.PEG0.PEGP.NVJT.JTCA */
                }
                Case (0x02)
                {
                    Debug = "   JT fun2 JT_FUNC_POLICYSELECT"
                    Return (0x80000002)
                }
                Case (0x03)
                {
                    Debug = "   JT fun3 JT_FUNC_POWERCONTROL"
                    CreateField (Arg3, Zero, 0x03, GPPC)
                    CreateField (Arg3, 0x04, One, PLPC)
                    CreateField (Arg3, 0x07, One, ECOC)
                    CreateField (Arg3, 0x0E, 0x02, DFGC)
                    CreateField (Arg3, 0x10, 0x03, GPCX)
                    \_SB.PC00.TGPC = Arg3
                    If (((ToInteger (GPPC) != Zero) || (ToInteger (DFGC
                        ) != Zero)))
                    {
                        \_SB.PC00.TDGC = ToInteger (DFGC)
                        \_SB.PC00.DGCX = ToInteger (GPCX)
                    }

                    Name (JTPC, Buffer (0x04)
                    {
                         0x00                                             // .
                    })
                    CreateField (JTPC, Zero, 0x03, GUPS)
                    CreateField (JTPC, 0x03, One, GPWO)
                    CreateField (JTPC, 0x07, One, PLST)
                    If ((ToInteger (DFGC) != Zero))
                    {
                        GPWO = One
                        GUPS = One
                        Return (JTPC) /* \_SB_.PC00.PEG0.PEGP.NVJT.JTPC */
                    }

                    Debug = "   JT fun3 GPPC="
                    Debug = ToInteger (GPPC)
                    If ((ToInteger (GPPC) == One))
                    {
                        \_SB.PC00.GC6I ()
                        PLST = One
                        GUPS = Zero
                    }
                    ElseIf ((ToInteger (GPPC) == 0x02))
                    {
                        \_SB.PC00.GC6I ()
                        If ((ToInteger (PLPC) == Zero))
                        {
                            PLST = Zero
                        }

                        GUPS = Zero
                    }
                    ElseIf ((ToInteger (GPPC) == 0x03))
                    {
                        \_SB.PC00.GC6O ()
                        If ((ToInteger (PLPC) != Zero))
                        {
                            PLST = Zero
                        }

                        GPWO = One
                        GUPS = One
                    }
                    ElseIf ((ToInteger (GPPC) == 0x04))
                    {
                        \_SB.PC00.GC6O ()
                        If ((ToInteger (PLPC) != Zero))
                        {
                            PLST = Zero
                        }

                        GPWO = One
                        GUPS = One
                    }
                    ElseIf ((\_SB.GGIV (PWGD) == One))
                    {
                        Debug = "   JT GETS() return 0x1"
                        GPWO = One
                        GUPS = One
                    }
                    Else
                    {
                        Debug = "   JT GETS() return 0x3"
                        GPWO = Zero
                        GUPS = 0x03
                    }

                    Return (JTPC) /* \_SB_.PC00.PEG0.PEGP.NVJT.JTPC */
                }
                Case (0x04)
                {
                    Debug = "   JT fun4 JT_FUNC_PLATPOLICY"
                    CreateField (Arg3, 0x02, One, PAUD)
                    CreateField (Arg3, 0x03, One, PADM)
                    CreateField (Arg3, 0x04, 0x04, PDGS)
                    Local0 = Zero
                    Local0 = (\_SB.PC00.PEG0.PEGP.HDAE << 0x02)
                    Return (Local0)
                }

            }

            Return (0x80000002)
        }
    }

    Scope (\_SB.PC00.PEG0.PEGP)
    {
        Name (GSV0, Buffer (One)
        {
             0x00                                             // .
        })
        Name (GSD0, Buffer (One)
        {
             0x00                                             // .
        })
        Name (GSV1, Buffer (0xD9)
        {
            /* 0000 */  0xAA, 0x75, 0xA5, 0x5F, 0x4D, 0xCE, 0x80, 0x9A,  // .u._M...
            /* 0008 */  0x4B, 0x56, 0xD9, 0x00, 0x00, 0x00, 0x01, 0x00,  // KV......
            /* 0010 */  0x39, 0x35, 0x32, 0x34, 0x36, 0x38, 0x32, 0x38,  // 95246828
            /* 0018 */  0x37, 0x37, 0x31, 0x36, 0x47, 0x65, 0x6E, 0x75,  // 7716Genu
            /* 0020 */  0x69, 0x6E, 0x65, 0x20, 0x4E, 0x56, 0x49, 0x44,  // ine NVID
            /* 0028 */  0x49, 0x41, 0x20, 0x43, 0x65, 0x72, 0x74, 0x69,  // IA Certi
            /* 0030 */  0x66, 0x69, 0x65, 0x64, 0x20, 0x47, 0x53, 0x79,  // fied GSy
            /* 0038 */  0x6E, 0x63, 0x20, 0x52, 0x65, 0x61, 0x64, 0x79,  // nc Ready
            /* 0040 */  0x20, 0x50, 0x6C, 0x61, 0x74, 0x66, 0x6F, 0x72,  //  Platfor
            /* 0048 */  0x6D, 0x20, 0x66, 0x6F, 0x72, 0x20, 0x41, 0x43,  // m for AC
            /* 0050 */  0x45, 0x52, 0x20, 0x4E, 0x42, 0x20, 0x33, 0x39,  // ER NB 39
            /* 0058 */  0x31, 0x35, 0x31, 0x36, 0x34, 0x20, 0x20, 0x20,  // 15164   
            /* 0060 */  0x20, 0x20, 0x20, 0x2D, 0x20, 0x43, 0x38, 0x52,  //    - C8R
            /* 0068 */  0x52, 0x33, 0x2D, 0x2C, 0x43, 0x5A, 0x4E, 0x5E,  // R3-,CZN^
            /* 0070 */  0x4C, 0x56, 0x44, 0x56, 0x29, 0x2E, 0x46, 0x34,  // LVDV).F4
            /* 0078 */  0x57, 0x2A, 0x30, 0x54, 0x54, 0x22, 0x5B, 0x40,  // W*0TT"[@
            /* 0080 */  0x5C, 0x3C, 0x54, 0x50, 0x5A, 0x42, 0x50, 0x46,  // \<TPZBPF
            /* 0088 */  0x39, 0x32, 0x3B, 0x5B, 0x55, 0x47, 0x25, 0x37,  // 92;[UG%7
            /* 0090 */  0x2B, 0x20, 0x2D, 0x20, 0x43, 0x6F, 0x70, 0x79,  // + - Copy
            /* 0098 */  0x72, 0x69, 0x67, 0x68, 0x74, 0x20, 0x32, 0x30,  // right 20
            /* 00A0 */  0x32, 0x32, 0x20, 0x4E, 0x56, 0x49, 0x44, 0x49,  // 22 NVIDI
            /* 00A8 */  0x41, 0x20, 0x43, 0x6F, 0x72, 0x70, 0x6F, 0x72,  // A Corpor
            /* 00B0 */  0x61, 0x74, 0x69, 0x6F, 0x6E, 0x20, 0x41, 0x6C,  // ation Al
            /* 00B8 */  0x6C, 0x20, 0x52, 0x69, 0x67, 0x68, 0x74, 0x73,  // l Rights
            /* 00C0 */  0x20, 0x52, 0x65, 0x73, 0x65, 0x72, 0x76, 0x65,  //  Reserve
            /* 00C8 */  0x64, 0x2D, 0x35, 0x32, 0x39, 0x33, 0x31, 0x34,  // d-529314
            /* 00D0 */  0x39, 0x32, 0x31, 0x39, 0x36, 0x31, 0x28, 0x52,  // 921961(R
            /* 00D8 */  0x29                                             // )
        })
        Name (GSV2, Buffer (0xD9)
        {
            /* 0000 */  0xE7, 0x33, 0x03, 0xFC, 0xE8, 0x14, 0xC1, 0x91,  // .3......
            /* 0008 */  0x4B, 0x56, 0xD9, 0x00, 0x00, 0x00, 0x01, 0x00,  // KV......
            /* 0010 */  0x39, 0x35, 0x32, 0x34, 0x36, 0x38, 0x32, 0x38,  // 95246828
            /* 0018 */  0x37, 0x37, 0x31, 0x36, 0x47, 0x65, 0x6E, 0x75,  // 7716Genu
            /* 0020 */  0x69, 0x6E, 0x65, 0x20, 0x4E, 0x56, 0x49, 0x44,  // ine NVID
            /* 0028 */  0x49, 0x41, 0x20, 0x43, 0x65, 0x72, 0x74, 0x69,  // IA Certi
            /* 0030 */  0x66, 0x69, 0x65, 0x64, 0x20, 0x47, 0x53, 0x79,  // fied GSy
            /* 0038 */  0x6E, 0x63, 0x20, 0x52, 0x65, 0x61, 0x64, 0x79,  // nc Ready
            /* 0040 */  0x20, 0x50, 0x6C, 0x61, 0x74, 0x66, 0x6F, 0x72,  //  Platfor
            /* 0048 */  0x6D, 0x20, 0x66, 0x6F, 0x72, 0x20, 0x41, 0x43,  // m for AC
            /* 0050 */  0x45, 0x52, 0x20, 0x4E, 0x42, 0x20, 0x33, 0x39,  // ER NB 39
            /* 0058 */  0x31, 0x35, 0x31, 0x36, 0x37, 0x20, 0x20, 0x20,  // 15167   
            /* 0060 */  0x20, 0x20, 0x20, 0x2D, 0x20, 0x46, 0x3B, 0x55,  //    - F;U
            /* 0068 */  0x51, 0x34, 0x2A, 0x2F, 0x4E, 0x5F, 0x32, 0x5D,  // Q4*/N_2]
            /* 0070 */  0x49, 0x5B, 0x43, 0x55, 0x34, 0x53, 0x49, 0x37,  // I[CU4SI7
            /* 0078 */  0x50, 0x29, 0x33, 0x20, 0x56, 0x27, 0x5E, 0x47,  // P)3 V'^G
            /* 0080 */  0x59, 0x21, 0x53, 0x5F, 0x25, 0x4F, 0x5D, 0x49,  // Y!S_%O]I
            /* 0088 */  0x3A, 0x35, 0x3E, 0x58, 0x58, 0x3B, 0x26, 0x32,  // :5>XX;&2
            /* 0090 */  0x56, 0x20, 0x2D, 0x20, 0x43, 0x6F, 0x70, 0x79,  // V - Copy
            /* 0098 */  0x72, 0x69, 0x67, 0x68, 0x74, 0x20, 0x32, 0x30,  // right 20
            /* 00A0 */  0x32, 0x32, 0x20, 0x4E, 0x56, 0x49, 0x44, 0x49,  // 22 NVIDI
            /* 00A8 */  0x41, 0x20, 0x43, 0x6F, 0x72, 0x70, 0x6F, 0x72,  // A Corpor
            /* 00B0 */  0x61, 0x74, 0x69, 0x6F, 0x6E, 0x20, 0x41, 0x6C,  // ation Al
            /* 00B8 */  0x6C, 0x20, 0x52, 0x69, 0x67, 0x68, 0x74, 0x73,  // l Rights
            /* 00C0 */  0x20, 0x52, 0x65, 0x73, 0x65, 0x72, 0x76, 0x65,  //  Reserve
            /* 00C8 */  0x64, 0x2D, 0x35, 0x32, 0x39, 0x33, 0x31, 0x34,  // d-529314
            /* 00D0 */  0x39, 0x32, 0x31, 0x39, 0x36, 0x31, 0x28, 0x52,  // 921961(R
            /* 00D8 */  0x29                                             // )
        })
        Name (GSD1, Buffer (0xD7)
        {
            /* 0000 */  0x2A, 0x28, 0xAE, 0x6D, 0x9F, 0xDE, 0x01, 0xAD,  // *(.m....
            /* 0008 */  0x52, 0x44, 0xD7, 0x00, 0x00, 0x00, 0x00, 0x01,  // RD......
            /* 0010 */  0x00, 0x00, 0x00, 0x00, 0xDE, 0x10, 0x00, 0x00,  // ........
            /* 0018 */  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  // ........
            /* 0020 */  0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x34, 0x00,  // ......4.
            /* 0028 */  0x00, 0x00, 0x01, 0x00, 0x47, 0x00, 0x00, 0x00,  // ....G...
            /* 0030 */  0x02, 0x00, 0x45, 0x00, 0x00, 0x00, 0x03, 0x00,  // ..E.....
            /* 0038 */  0x87, 0x00, 0x00, 0x00, 0x04, 0x00, 0x85, 0x00,  // ........
            /* 0040 */  0x00, 0x00, 0x05, 0x00, 0x83, 0x00, 0x00, 0x00,  // ........
            /* 0048 */  0x06, 0x00, 0x81, 0x00, 0x00, 0x00, 0x07, 0x00,  // ........
            /* 0050 */  0x7F, 0x00, 0x00, 0x00, 0x08, 0x00, 0x7D, 0x00,  // ......}.
            /* 0058 */  0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0xD9, 0x1C,  // ........
            /* 0060 */  0x04, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00,  // ........
            /* 0068 */  0x41, 0x5D, 0xC9, 0x00, 0x01, 0x24, 0x2E, 0x00,  // A]...$..
            /* 0070 */  0x02, 0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x01,  // ........
            /* 0078 */  0x00, 0x00, 0x00, 0xD9, 0x1C, 0x04, 0x00, 0x00,  // ........
            /* 0080 */  0x00, 0x02, 0x00, 0x00, 0x00, 0xE0, 0x7C, 0x97,  // ......|.
            /* 0088 */  0x01, 0xC4, 0xD5, 0xC4, 0x32, 0x00, 0x00, 0x00,  // ....2...
            /* 0090 */  0x00, 0x00, 0x00, 0x00, 0x00, 0x26, 0x00, 0x00,  // .....&..
            /* 0098 */  0x00, 0x31, 0x00, 0x36, 0x00, 0x35, 0x00, 0x2A,  // .1.6.5.*
            /* 00A0 */  0x00, 0x31, 0x00, 0x34, 0x00, 0x35, 0x00, 0x34,  // .1.4.5.4
            /* 00A8 */  0x00, 0x35, 0x00, 0x3B, 0x00, 0x36, 0x00, 0x30,  // .5.;.6.0
            /* 00B0 */  0x00, 0x2A, 0x00, 0x34, 0x00, 0x30, 0x00, 0x30,  // .*.4.0.0
            /* 00B8 */  0x00, 0x30, 0x00, 0x30, 0x00, 0x00, 0x00, 0x00,  // .0.0....
            /* 00C0 */  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  // ........
            /* 00C8 */  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  // ........
            /* 00D0 */  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00         // .......
        })
        Method (NBCI, 4, Serialized)
        {
            Debug = "------- NV NBCI DSM --------"
            If ((Arg1 != 0x0102))
            {
                Debug = " NBCI DSM: NOT SUPPORTED!"
                Return (0x80000002)
            }

            If ((Arg2 == Zero))
            {
                Debug = "   NBCI fun0 NBCI_FUNC_SUPPORT"
                Return (Buffer (0x04)
                {
                     0x01, 0x00, 0x11, 0x00                           // ....
                })
            }

            If ((Arg2 == 0x10))
            {
                Debug = "   NBCI fun16 NBCI_FUNC_GETOBJBYTYPE"
                CreateWordField (Arg3, 0x02, BFF0)
                If ((BFF0 == 0x564B))
                {
                    If ((((\_SB.VSID == 0x03) && (\_SB.CPUI == 0x02)) && (\_SB.CDSB == 0x11)))
                    {
                        Return (GSV1) /* \_SB_.PC00.PEG0.PEGP.GSV1 */
                    }
                    ElseIf ((((\_SB.VSID == One) && (\_SB.CPUI == 0x02)) && (\_SB.CDSB == 
                        0x11)))
                    {
                        Return (GSV2) /* \_SB_.PC00.PEG0.PEGP.GSV2 */
                    }
                    Else
                    {
                        Return (GSV0) /* \_SB_.PC00.PEG0.PEGP.GSV0 */
                    }
                }

                If ((BFF0 == 0x4452))
                {
                    If ((\_SB.CDSB == 0x11))
                    {
                        Return (GSD1) /* \_SB_.PC00.PEG0.PEGP.GSD1 */
                    }
                    Else
                    {
                        Return (GSD0) /* \_SB_.PC00.PEG0.PEGP.GSD0 */
                    }
                }
            }

            If ((Arg2 == 0x14))
            {
                Debug = "   NBCI fun20 NBCI_FUNC_GETBACKLIGHT"
                Return (Package (0x20)
                {
                    0x8000A450, 
                    0x0200, 
                    Zero, 
                    Zero, 
                    0x04, 
                    One, 
                    0x03E8, 
                    0x3C, 
                    0x03E8, 
                    0x0B, 
                    0x3C, 
                    0xB4, 
                    0x012C, 
                    0x015E, 
                    0x01B8, 
                    0x0212, 
                    0x026C, 
                    0x02D0, 
                    0x032A, 
                    0x038E, 
                    0x03E8, 
                    Zero, 
                    0x64, 
                    0xC8, 
                    0x012C, 
                    0x0190, 
                    0x01F4, 
                    0x0258, 
                    0x02BC, 
                    0x0320, 
                    0x0384, 
                    0x03E8
                })
            }
        }
    }

    Scope (\_SB)
    {
        Device (NPCF)
        {
            Name (ACBT, Zero)
            Name (DCBT, Zero)
            Name (DBAC, Zero)
            Name (DBDC, Zero)
            Name (AMAT, 0x78)
            Name (AMIT, Zero)
            Name (ATPP, 0xF0)
            Name (DTPP, Zero)
            Name (TPPL, Zero)
            Name (DROS, Zero)
            Name (LTBL, Zero)
            Name (STBL, Zero)
            Name (NVWM, Zero)
            Name (LCTP, Zero)
            Name (LGTP, Zero)
            Name (LETP, Zero)
            Name (CIDX, Zero)
            Name (GIDX, Zero)
            Name (EIDX, 0x06)
            Method (CTBT, 0, Serialized)
            {
                Local0 = \_SB.PC00.LPCB.EC0.CTMP /* External reference */
                If ((CIDX == Zero))
                {
                    If ((Local0 >= 0x36))
                    {
                        CIDX = One
                    }
                }
                ElseIf ((CIDX == One))
                {
                    If ((Local0 >= 0x3A))
                    {
                        CIDX = 0x02
                    }

                    If ((Local0 < 0x32))
                    {
                        CIDX = Zero
                    }
                }
                ElseIf ((CIDX == 0x02))
                {
                    If ((Local0 >= 0x41))
                    {
                        CIDX = 0x03
                    }

                    If ((Local0 < 0x36))
                    {
                        CIDX = One
                    }
                }
                ElseIf ((CIDX == 0x03))
                {
                    If ((Local0 >= 0x63))
                    {
                        CIDX = 0x04
                    }

                    If ((Local0 < 0x3A))
                    {
                        CIDX = 0x02
                    }
                }
                ElseIf ((CIDX == 0x04))
                {
                    If ((Local0 < 0x41))
                    {
                        CIDX = 0x03
                    }
                }

                LCTP = Local0
                Return ((((Local0 * 0x0100) << 0x08) + CIDX))
            }

            Method (GTBT, 0, Serialized)
            {
                Local1 = \_SB.PC00.LPCB.EC0.GTMP /* External reference */
                If ((GIDX == Zero))
                {
                    If ((Local1 >= 0x3C))
                    {
                        GIDX = One
                    }
                }
                ElseIf ((GIDX == One))
                {
                    If ((Local1 >= 0x41))
                    {
                        GIDX = 0x02
                    }

                    If ((Local1 < 0x32))
                    {
                        GIDX = Zero
                    }
                }
                ElseIf ((GIDX == 0x02))
                {
                    If ((Local1 >= 0x46))
                    {
                        GIDX = 0x03
                    }

                    If ((Local1 < 0x3C))
                    {
                        GIDX = One
                    }
                }
                ElseIf ((GIDX == 0x03))
                {
                    If ((Local1 >= 0x4B))
                    {
                        GIDX = 0x04
                    }

                    If ((Local1 < 0x41))
                    {
                        GIDX = 0x02
                    }
                }
                ElseIf ((GIDX == 0x04))
                {
                    If ((Local1 >= 0x63))
                    {
                        GIDX = 0x05
                    }

                    If ((Local1 < 0x46))
                    {
                        GIDX = 0x03
                    }
                }
                ElseIf ((GIDX == 0x05))
                {
                    If ((Local1 < 0x4B))
                    {
                        GIDX = 0x04
                    }
                }

                LGTP = Local1
                Return ((((Local1 * 0x0100) << 0x08) + GIDX))
            }

            Name (CDIS, Zero)
            Name (CUSL, Zero)
            Name (CUCT, Zero)
            Method (_HID, 0, NotSerialized)  // _HID: Hardware ID
            {
                CDIS = Zero
                Return ("NVDA0820")
            }

            Name (_UID, "NPCF")  // _UID: Unique ID
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If ((CDIS == One))
                {
                    Return (0x0D)
                }

                Return (0x0F)
            }

            Method (_DIS, 0, NotSerialized)  // _DIS: Disable Device
            {
                CDIS = One
            }

            Method (_DSM, 4, Serialized)  // _DSM: Device-Specific Method
            {
                If ((Arg0 == ToUUID ("36b49710-2483-11e7-9598-0800200c9a66") /* Unknown UUID */))
                {
                    If ((\_SB.PC00.PEG0.PEGP.NPCS != Zero))
                    {
                        Return (NPCF (Arg0, Arg1, Arg2, Arg3))
                    }
                }
            }

            Method (NPCF, 4, Serialized)
            {
                Debug = "------- NVPCF DSM --------"
                If ((ToInteger (Arg1) != 0x0200))
                {
                    Return (0x80000001)
                }

                Switch (ToInteger (Arg2))
                {
                    Case (Zero)
                    {
                        Debug = "   NVPCF sub-func#0"
                        Return (Buffer (0x04)
                        {
                             0x3F, 0x07, 0x00, 0x00                           // ?...
                        })
                    }
                    Case (One)
                    {
                        Debug = "   NVPCF sub-func#1"
                        Return (Buffer (0x0E)
                        {
                            /* 0000 */  0x20, 0x03, 0x01, 0x00, 0x23, 0x04, 0x05, 0x01,  //  ...#...
                            /* 0008 */  0x01, 0x01, 0x00, 0x00, 0x00, 0xAD               // ......
                        })
                    }
                    Case (0x02)
                    {
                        Debug = "   NVPCF sub-func#2"
                        Name (PBD2, Buffer (0x31)
                        {
                             0x00                                             // .
                        })
                        CreateByteField (PBD2, Zero, PTV2)
                        CreateByteField (PBD2, One, PHB2)
                        CreateByteField (PBD2, 0x02, GSB2)
                        CreateByteField (PBD2, 0x03, CTB2)
                        CreateByteField (PBD2, 0x04, NCE2)
                        PTV2 = 0x23
                        PHB2 = 0x05
                        GSB2 = 0x10
                        CTB2 = 0x1C
                        NCE2 = One
                        CreateWordField (PBD2, 0x05, TGPA)
                        CreateWordField (PBD2, 0x07, TGPD)
                        CreateByteField (PBD2, 0x15, PC01)
                        CreateByteField (PBD2, 0x16, PC02)
                        CreateWordField (PBD2, 0x19, TPPA)
                        CreateWordField (PBD2, 0x1B, TPPD)
                        CreateWordField (PBD2, 0x1D, MAGA)
                        CreateWordField (PBD2, 0x1F, MAGD)
                        CreateWordField (PBD2, 0x21, MIGA)
                        CreateWordField (PBD2, 0x23, MIGD)
                        CreateDWordField (PBD2, 0x29, LTBC)
                        CreateDWordField (PBD2, 0x2D, STBC)
                        CreateField (Arg3, 0x28, 0x02, NIGS)
                        CreateByteField (Arg3, 0x15, IORC)
                        CreateField (Arg3, 0xB0, One, PWCS)
                        CreateField (Arg3, 0xB1, One, PWTS)
                        CreateField (Arg3, 0xB2, One, CGPS)
                        If ((ToInteger (NIGS) == Zero))
                        {
                            TGPA = ACBT /* \_SB_.NPCF.ACBT */
                            TGPD = DCBT /* \_SB_.NPCF.DCBT */
                            PC01 = Zero
                            If ((\_SB.VSID == One))
                            {
                                DBDC = One
                            }
                            Else
                            {
                                DBDC = Zero
                            }

                            PC02 = (DBAC | (DBDC << One))
                            TPPA = ATPP /* \_SB_.NPCF.ATPP */
                            TPPD = DTPP /* \_SB_.NPCF.DTPP */
                            MAGA = AMAT /* \_SB_.NPCF.AMAT */
                            MIGA = AMIT /* \_SB_.NPCF.AMIT */
                        }

                        If ((ToInteger (NIGS) == One))
                        {
                            If ((ToInteger (PWCS) == One)){}
                            Else
                            {
                            }

                            If ((ToInteger (PWTS) == One)){}
                            Else
                            {
                            }

                            If ((ToInteger (CGPS) == One)){}
                            Else
                            {
                            }

                            TGPA = Zero
                            TGPD = Zero
                            PC01 = Zero
                            PC02 = Zero
                            TPPA = Zero
                            TPPD = Zero
                            MAGA = Zero
                            MIGA = Zero
                            MAGD = Zero
                            MIGD = Zero
                        }

                        Return (PBD2) /* \_SB_.NPCF.NPCF.PBD2 */
                    }
                    Case (0x03)
                    {
                        Debug = "   NVPCF sub-func#3"
                        Return (Buffer (0x2A)
                        {
                            /* 0000 */  0x11, 0x04, 0x13, 0x02, 0x00, 0xFF, 0x00, 0x32,  // .......2
                            /* 0008 */  0x36, 0x36, 0x3A, 0x3A, 0x41, 0x41, 0x63, 0xFF,  // 66::AAc.
                            /* 0010 */  0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x05,  // ........
                            /* 0018 */  0xFF, 0x00, 0x32, 0x3C, 0x3C, 0x41, 0x41, 0x46,  // ..2<<AAF
                            /* 0020 */  0x46, 0x4B, 0x4B, 0x63, 0xFF, 0xFF, 0xFF, 0xFF,  // FKKc....
                            /* 0028 */  0xFF, 0xFF                                       // ..
                        })
                    }
                    Case (0x04)
                    {
                        Debug = "   NVPCF sub-func#4"
                        Return (Buffer (0x2C)
                        {
                            /* 0000 */  0x11, 0x04, 0x29, 0x01, 0x05, 0x00, 0x01, 0x02,  // ..).....
                            /* 0008 */  0x03, 0x04, 0x03, 0x01, 0x02, 0x03, 0x00, 0x01,  // ........
                            /* 0010 */  0x02, 0x03, 0x04, 0x04, 0x00, 0x01, 0x02, 0x03,  // ........
                            /* 0018 */  0x04, 0x04, 0x00, 0x01, 0x02, 0x03, 0x04, 0x04,  // ........
                            /* 0020 */  0x00, 0x01, 0x02, 0x03, 0x04, 0x04, 0x04, 0x04,  // ........
                            /* 0028 */  0x04, 0x04, 0x04, 0x04                           // ....
                        })
                    }
                    Case (0x05)
                    {
                        Debug = "   NVPCF sub-func#5"
                        Name (PBD5, Buffer (0x28)
                        {
                             0x00                                             // .
                        })
                        CreateByteField (PBD5, Zero, PTV5)
                        CreateByteField (PBD5, One, PHB5)
                        CreateByteField (PBD5, 0x02, TEB5)
                        CreateByteField (PBD5, 0x03, NTE5)
                        PTV5 = 0x11
                        PHB5 = 0x04
                        TEB5 = 0x24
                        NTE5 = One
                        CreateDWordField (PBD5, 0x04, F5O0)
                        CreateDWordField (PBD5, 0x08, F5O1)
                        CreateDWordField (PBD5, 0x0C, F5O2)
                        CreateDWordField (PBD5, 0x10, F5O3)
                        CreateDWordField (PBD5, 0x14, F5O4)
                        CreateDWordField (PBD5, 0x18, F5O5)
                        CreateDWordField (PBD5, 0x1C, F5O6)
                        CreateDWordField (PBD5, 0x20, F5O7)
                        CreateDWordField (PBD5, 0x24, F5O8)
                        CreateField (Arg3, 0x20, 0x03, INC5)
                        CreateDWordField (Arg3, 0x08, F5P1)
                        CreateDWordField (Arg3, 0x0C, F5P2)
                        Switch (ToInteger (INC5))
                        {
                            Case (Zero)
                            {
                                F5O0 = NVWM /* \_SB_.NPCF.NVWM */
                                F5O1 = Zero
                                F5O2 = Zero
                                F5O3 = Zero
                            }
                            Case (One)
                            {
                                F5O0 = 0x0C
                                F5O1 = Zero
                                F5O2 = Zero
                                F5O3 = Zero
                            }
                            Case (0x02)
                            {
                                F5O0 = Zero
                                F5O1 = CTBT ()
                                F5O2 = GTBT ()
                                F5O3 = Zero
                                F5O4 = Zero
                                F5O5 = Zero
                                F5O6 = Zero
                                F5O7 = Zero
                                F5O8 = Zero
                            }
                            Case (0x03)
                            {
                                CUSL = (F5P1 & 0xFF)
                            }
                            Case (0x04)
                            {
                                CUCT = F5P2 /* \_SB_.NPCF.NPCF.F5P2 */
                            }
                            Default
                            {
                                Return (0x80000002)
                            }

                        }

                        Return (PBD5) /* \_SB_.NPCF.NPCF.PBD5 */
                    }
                    Case (0x07)
                    {
                        Debug = "   NVPCF sub-func#7"
                        CreateDWordField (Arg3, 0x05, AMAX)
                        CreateDWordField (Arg3, 0x09, ARAT)
                        CreateDWordField (Arg3, 0x0D, DMAX)
                        CreateDWordField (Arg3, 0x11, DRAT)
                        CreateDWordField (Arg3, 0x15, TGPM)
                        Return (Zero)
                    }
                    Case (0x08)
                    {
                        Debug = "   NVPCF sub-func#8"
                        Name (PBD8, Buffer (0x37)
                        {
                             0x00                                             // .
                        })
                        CreateByteField (PBD8, Zero, PTV8)
                        CreateByteField (PBD8, One, PHB8)
                        CreateByteField (PBD8, 0x02, TEB8)
                        CreateByteField (PBD8, 0x03, NTE8)
                        PTV8 = 0x10
                        PHB8 = 0x04
                        TEB8 = 0x11
                        NTE8 = 0x03
                        CreateByteField (PBD8, 0x04, FP10)
                        CreateDWordField (PBD8, 0x05, FP11)
                        CreateDWordField (PBD8, 0x09, FP12)
                        CreateDWordField (PBD8, 0x0D, FP13)
                        CreateDWordField (PBD8, 0x11, FP14)
                        CreateByteField (PBD8, 0x15, FP20)
                        CreateDWordField (PBD8, 0x16, FP21)
                        CreateDWordField (PBD8, 0x1A, FP22)
                        CreateDWordField (PBD8, 0x1E, FP23)
                        CreateDWordField (PBD8, 0x22, FP24)
                        CreateByteField (PBD8, 0x26, FP30)
                        CreateDWordField (PBD8, 0x27, FP31)
                        CreateDWordField (PBD8, 0x2B, FP32)
                        CreateDWordField (PBD8, 0x2F, FP33)
                        CreateDWordField (PBD8, 0x33, FP34)
                        FP10 = 0x64
                        FP11 = 0x12C0
                        FP12 = 0x61A8
                        FP13 = 0x4E20
                        FP14 = 0x7530
                        FP20 = 0x46
                        FP21 = 0x12C0
                        FP22 = 0x5DC0
                        FP23 = 0x4E20
                        FP24 = 0x7530
                        FP30 = 0x32
                        FP31 = 0x12C0
                        FP32 = 0x59D8
                        FP33 = 0x4E20
                        FP34 = 0x7530
                        Return (PBD8) /* \_SB_.NPCF.NPCF.PBD8 */
                    }
                    Case (0x09)
                    {
                        Debug = "   NVPCF sub-func#9"
                        CreateDWordField (Arg3, 0x03, CPTD)
                        Acquire (NVZZ, 0xFFFF)
                        If ((CPTD != Zero))
                        {
                            Local0 = (CPTD / 0x03E8)
                            Local1 = (Local0 * 0x08)
                            Local2 = (Local1 >> 0x08)
                            \_SB.PC00.LPCB.EC0.DP1H = Local2
                            \_SB.PC00.LPCB.EC0.DP1L = Local1
                            \_SB.PC00.LPCB.EC0.DP2H = Local2
                            \_SB.PC00.LPCB.EC0.DP2L = Local1
                            \_SB.PC00.LPCB.EC0.EC6E (0xA0)
                            \_SB.PC00.LPCB.EC0.ECDW (0x0E)
                        }
                        Else
                        {
                            \_SB.PC00.LPCB.EC0.EC6E (0xA0)
                            \_SB.PC00.LPCB.EC0.ECDW (0x0D)
                            \_SB.PC00.LPCB.EC0.DP1H = Zero
                            \_SB.PC00.LPCB.EC0.DP1L = Zero
                            \_SB.PC00.LPCB.EC0.DP2H = Zero
                            \_SB.PC00.LPCB.EC0.DP2L = Zero
                        }

                        Release (NVZZ)
                        Return (Zero)
                    }
                    Case (0x0A)
                    {
                        Debug = "   NVPCF sub-func#10"
                        Name (PBDA, Buffer (0x08)
                        {
                             0x00                                             // .
                        })
                        CreateByteField (PBDA, Zero, DTTV)
                        CreateByteField (PBDA, One, DTSH)
                        CreateByteField (PBDA, 0x02, DTSE)
                        CreateByteField (PBDA, 0x03, DTTE)
                        CreateDWordField (PBDA, 0x04, DTTL)
                        DTTV = 0x10
                        DTSH = 0x04
                        DTSE = 0x04
                        DTTE = One
                        DTTL = TPPL /* \_SB_.NPCF.TPPL */
                        Return (PBDA) /* \_SB_.NPCF.NPCF.PBDA */
                    }

                }

                Return (0x80000002)
            }

            Mutex (NVZZ, 0x00)
        }
    }
}

