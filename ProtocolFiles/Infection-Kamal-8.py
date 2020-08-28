from opentrons import protocol_api

metadata = {
    'protocolName': 'Infection Protocol 8 (Kamal)',
    'author': 'Chris Sutanto',
    'description': '[8 of 8] Aspirate supernatant from plate 3, then add 100 uL PBS to each well and mix 3 times',
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
    PBS_well = 0 # Location of PBS in reservoir, 0-based indexing (left most well is 0)
    trash_well = 11 # Location of trash in reservoir, 0-based indexing (left most well is 0)
    remove_volume = 10 # Volume to remove from each well, be careful to not aspirate too much to disturb the pellet [uL]
    PBS_volume = 100 # Volume of PBS to add to each well of plate 3 [uL]
    # end modify
    
    # other values
    mix_count = 3 
    mix_volume = 50
    wellplate_3_columns = [wellplate_3.columns()[i] for i in range(0, 12)]
    wellplate_3_columns_reversed = wellplate_3_columns[::-1]
    
    # commands
    # 1. Aspirate supernatant from plate 3, discard
    p50_multi.pick_up_tip()
    p50_multi.transfer(
        remove_volume,
        wellplate_3_columns_reversed,
        reservoir.wells()[trash_well],
        new_tip='never'
    )
    p50_multi.drop_tip()

    # 2. Add 100 uL PBS to each well of plate 3, mix 3 times
    p300_multi.pick_up_tip()
    p300_multi.transfer(
        PBS_volume,
        reservoir.wells()[PBS_well],
        wellplate_3_columns_reversed,
        new_tip='never',
        mix_after=(mix_count, mix_volume)
    )
    p300_multi.drop_tip()