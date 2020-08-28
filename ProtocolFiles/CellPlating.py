from opentrons import protocol_api

metadata = {
    'protocolName': 'Cell Plating',
    'author': 'Chris Sutanto',
    'description': 'Aliquot cells from 12-well reservoir into a 96-well plate',
    'apiLevel': '2.2',
}

def run(protocol:protocol_api.ProtocolContext):

    # labware
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', '4')
    well_plate = protocol.load_labware('appliedbiosystems_96_wellplate_200ul', '5')
    tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', '10')

    # pipettes
    p300_multi = protocol.load_instrument('p300_multi', 'left', tip_racks = [tiprack])
    p50_multi = protocol.load_instrument('p50_multi', 'right')

    # modify
    source_well = 0 # Location of source in reservoir, 0-based indexing (left most well is 0)
    volume_per_well = 200 # Amount to distribute into each well [uL]
    mix_count = 5 # Number of times to mix before aspirating
    mix_volume = 100 # Volume to mix before aspirating [uL]
    # end modify

    # commands
    p300_multi.pick_up_tip()
    for i in range(12):
        p300_multi.distribute(
            volume_per_well,
            reservoir.wells()[source_well],
            well_plate.columns()[i],
            mix_before=(mix_count, mix_volume),
            new_tip='never',
            disposal_volume=0)
    p300_multi.return_tip()