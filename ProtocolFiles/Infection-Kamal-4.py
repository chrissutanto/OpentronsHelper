from opentrons import protocol_api

metadata = {
    'protocolName': 'Infection Protocol 4 (Kamal)',
    'author': 'Chris Sutanto',
    'description': '[4 of 8] Adds 50 uL of media to wells in plate 2, mixes each well, then transfers 100 uL into wells of plate 3.',
    'apiLevel': '2.2'
}

def run(protocol:protocol_api.ProtocolContext):

    # labware
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', '4')
    wellplate_2 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '5')
    wellplate_3 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '6')
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_300ul', '11')

    # pipettes
    p300_multi = protocol.load_instrument('p300_multi', 'left', tip_racks = [tiprack_1, tiprack_2])
    p50_multi = protocol.load_instrument('p50_multi', 'right', tip_racks = [tiprack_1, tiprack_2])

    # modify
    media_well = 0 # Location of media in reservoir, 0-based indexing (left most well is 0)
    media_volume = 50 # Volume of media to add to each well of plate 2 [uL]
    transfer_volume = 100 # Volume to transfer from wells in plate 2 to corresponing wells in plate 3 [uL]
    # end modify

    # other values
    mix_count = 3 
    mix_volume = 25
    wellplate_2_columns = [wellplate_2.columns()[i] for i in range(0, 12)]
    wellplate_3_columns = [wellplate_3.columns()[i] for i in range(0, 12)]
    wellplate_2_columns_reversed = wellplate_2_columns[::-1]
    wellplate_3_columns_reversed = wellplate_3_columns[::-1]

    # commands
    # 1. Add 50 uL of media to each well in plate 2
    p50_multi.pick_up_tip()
    p50_multi.transfer(
        media_volume,
        reservoir.wells()[media_well],
        wellplate_2_columns_reversed,
        new_tip='never'
    )
    p50_multi.drop_tip()

    # 2. Mix three times, then transfer 100 uL from plate 2 into the corresponding well of plate 3
    p300_multi.pick_up_tip()
    for i in range(0, 12):
        p300_multi.transfer(
            transfer_volume,
            wellplate_2_columns_reversed[i],
            wellplate_3_columns_reversed[i],
            new_tip='never',
            mix_before=(mix_count, mix_volume)
        )
    p300_multi.drop_tip()