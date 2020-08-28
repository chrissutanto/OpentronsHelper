from opentrons import protocol_api

metadata = {
    'protocolName': 'Infection Protocol 7 (Kamal)',
    'author': 'Chris Sutanto',
    'description': '[7 of 8] Remove supernatant from each well of plate 3, then add 10 uL of secondary antibody mix to each well.',
    'apiLevel': '2.2'
}

def run(protocol:protocol_api.ProtocolContext):

    # labware
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', '4')
    wellplate_3 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '5')
    tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', '10')

    # pipettes
    p300_multi = protocol.load_instrument('p300_multi', 'left', tip_racks = [tiprack])
    p50_multi = protocol.load_instrument('p50_multi', 'right', tip_racks = [tiprack])

    # modify
    antibody_well = 0 # Location of secondary antibody mix in reservoir, 0-based indexing (left most well is 0)
    trash_well = 11 # Location of trash in reservoir, 0-based indexing (left most well is 0)
    remove_volume = 100 # Volume to remove from each well, be careful to not aspirate too much to disturb the pellet [uL]
    antibody_volume = 10 # Volume of secondary antibody mix to add to each well of plate 3 [uL]
    # end modify

    # other values
    wellplate_3_columns = [wellplate_3.columns()[i] for i in range(0, 12)]
    wellplate_3_columns_reversed = wellplate_3_columns[::-1]

    # commands
    # 1. Aspirate supernatant from plate 3, discard
    p300_multi.pick_up_tip()
    p300_multi.transfer(
        remove_volume,
        wellplate_3_columns_reversed,
        reservoir.wells()[trash_well],
        new_tip='never'
    )
    p300_multi.drop_tip()

    # 2. Add 10 uL of secondary antibody mix to each well in plate 3
    p50_multi.pick_up_tip()
    p50_multi.transfer(
        antibody_volume,
        reservoir.wells()[antibody_well],
        wellplate_3_columns_reversed,
        new_tip='never'
    )
    p50_multi.drop_tip()