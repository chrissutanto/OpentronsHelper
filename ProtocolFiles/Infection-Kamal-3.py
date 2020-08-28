from opentrons import protocol_api

metadata = {
    'protocolName': 'Infection Protocol 3 (Kamal)',
    'author': 'Chris Sutanto',
    'description': '[3 of 8] Remove 100 uL from plate 2, washes plate 2 (3 times), then adds 50 uL of Trypsin EDTA.',
    'apiLevel': '2.2'
}

def run(protocol:protocol_api.ProtocolContext):

    # labware 
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', '4')
    wellplate_2 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '6')
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_300ul', '11')

    # pipettes
    p300_multi = protocol.load_instrument('p300_multi', 'left', tip_racks = [tiprack_1, tiprack_2])
    p50_multi = protocol.load_instrument('p50_multi', 'right', tip_racks = [tiprack_1, tiprack_2])

    # modify
    PBS_well = [2, 3, 4] # Locations of PBS in reservoir, 0-based indexing (left most well is 0)
    TrypsinEDTA_well = 7 # Location of Trypsin-EDTA in reservoir, 0-based indexing (left most well is 0)
    trash_well = [8, 9, 10, 11] # Location of trash in reservoir, 0-based indexing (left most well is 0)
    remove_volume = 100 # Volume to remove from each well of plate 2 prior to washing [uL]
    wash_volume = 200 # Volume of PBS to use per well for each wash [uL]
    TrypsinEDTA_volume = 50 # Volume of Trypsin-EDTA to add per each well [uL]
    # end modify

    # other values
    wellplate_2_columns = [wellplate_2.columns()[i] for i in range(0, 12)]
    wellplate_2_columns_reversed = wellplate_2_columns[::-1]

    # commands
    # 1. Aspirate 100 uL from each well in plate 2 and discard
    p300_multi.pick_up_tip()
    p300_multi.consolidate(
        remove_volume, 
        wellplate_2_columns_reversed,
        reservoir.wells()[trash_well[3]],
        new_tip='never'
    )
    p300_multi.drop_tip()

    # 2. Wash plate 2 with 200 uL PBS three times
    for i in range(3):
        p300_multi.pick_up_tip()
        p300_multi.transfer(
            wash_volume,
            reservoir.wells()[PBS_well[i]],
            wellplate_2_columns_reversed,
            new_tip='never',
        )
        p300_multi.drop_tip()
        p300_multi.pick_up_tip()
        p300_multi.transfer(
            wash_volume,
            wellplate_2_columns_reversed,
            reservoir.wells()[trash_well[i]],
            new_tip='never'
        )
        p300_multi.drop_tip()

    # 3. Add 50 uL of Trypsin-EDTA to each well in plate 2
    p300_multi.pick_up_tip()
    p50_multi.transfer(
        TrypsinEDTA_volume,
        reservoir.wells()[TrypsinEDTA_well],
        wellplate_2_columns_reversed
    )
    p300_multi.drop_tip()