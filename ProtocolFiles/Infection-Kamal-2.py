from opentrons import protocol_api

metadata = {
    'protocolName': 'Infection Protocol 2 (Kamal)',
    'author': 'Chris Sutanto',
    'description': '[2 of 8] Removes 125 uL from plate 2, then transfers 25 from each well in plate 1 to plate 2.',
    'apiLevel': '2.2'
}

def run(protocol:protocol_api.ProtocolContext):
    
    # labware
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', '4')
    wellplate_1 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '5')
    wellplate_2 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '6')
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_300ul', '11')

    # pipettes
    p300_multi = protocol.load_instrument('p300_multi', 'left', tip_racks = [tiprack_1, tiprack_2])
    p50_multi = protocol.load_instrument('p50_multi', 'right', tip_racks = [tiprack_1, tiprack_2])

    # modify
    remove_volume = 125 # Volume to remove and discard from each well of plate 2 [uL]
    transfer_volume = 25 # Volume to transfer from each well in plate 1 to the corresponding well of plate 2 [uL]
    trash_well = 11 # Location of trash in reservoir, 0-based indexing (left most well is 0)
    # end modify

    # other values
    wellplate_1_columns = [wellplate_1.columns()[i] for i in range(0, 12)]
    wellplate_2_columns = [wellplate_2.columns()[i] for i in range(0, 12)]
    wellplate_1_columns_reversed = wellplate_1_columns[::-1]
    wellplate_2_columns_reversed = wellplate_2_columns[::-1]

    # commands
    # 1. Aspirate and discard 125 uL from each well of plate 2
    p300_multi.pick_up_tip()
    p300_multi.consolidate(
        remove_volume,
        wellplate_2_columns_reversed,
        reservoir.wells()[trash_well],
        new_tip='never'
    )
    p300_multi.drop_tip()

    # 2. Add 25 uL from each well in plate 1 to the corresponding well in plate 2
    for i in range(0, 12):
        p50_multi.pick_up_tip()
        p50_multi.transfer(
            transfer_volume,
            wellplate_1_columns_reversed[i],
            wellplate_2_columns_reversed[i],
            new_tip='never'
        )
        p50_multi.drop_tip()
