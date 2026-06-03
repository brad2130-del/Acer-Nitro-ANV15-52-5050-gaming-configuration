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
        Method (_INI, 0, NotSerialized)
        {
            AMAT = 0x7530  // 300W AC max
            ACBT = 0x1D4C  // 75W battery
            ATPP = 0x7D00  // 320W total platform
            DBAC = One
            DBDC = Zero
            NVWM = One
            DCBT = 0x1388  // 50W on battery
            DTPP = 0x1388  // 50W total on battery
        }
    }
}
