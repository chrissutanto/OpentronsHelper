from opentrons import protocol_api

metadata = {
    'protocolName': 'Infection Protocol 1 (Kamal)',
    'author': 'Chris Sutanto',
    'description': '[1 of 8] Serial dilution of antibodies in PBS, then plates sporozoites with FBS.',
    'apiLevel': '2.2'
}

def run(protocol:protocol_api.ProtocolContext):
    
    # labware
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', '4')
    wellplate_1 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '5')
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    tiprack_2 = protocol.load_labware('opentrons_96_tiprack_300ul', '11')

    # pipettes
    p300_multi = protocol.load_instrument('p300_multi', 'left', tip_racks = [tiprack_1, tiprack_2])
    p50_multi = protocol.load_instrument('p50_multi', 'right', tip_racks = [tiprack_1, tiprack_2])

    # modify
    antibodies_well = 0 # Location of antibodies in reservoir, 0-based indexing (left most well is 0)
    PBS_well = 2 # Location of PBS in reservoir, 0-based indexing (left most well is 0)
    sporozoites_well = 4 # Location of sporozoites in reservoir, 0-based indexing (left most well is 0)
    FBS_well = 6 # Location of FBS in reservoir, 0-based indexing (left most well is 0)
    trash_well = 11 # Location of trash in reservoir, 0-based indexing (left most well is 0)
    antibodies_volume = 20 # Volume of antibodies per well in columns 1 and 2 before dilution[uL]
    PBS_volume = 10 # Volume of PBS per well in columns 3-12 before dilution[uL]
    sporozoites_volume = 10 # Volume of sporozoites per well [uL]
    FBS_volume = 5 # Volume of FBS per well [uL]
    # end modify

    # other values
    dilute_volume = 10
    mix_count = 10
    mix_volume = 10
    wellplate_1_columns = [wellplate_1.columns()[i] for i in range(0, 12)]
    wellplate_1_columns_reversed = wellplate_1_columns[::-1]


    # commands
    # 1. Aliquot antibodies into columns 1 and 2 of plate 1
    p50_multi.pick_up_tip()
    p50_multi.distribute(
        antibodies_volume,
        reservoir.wells()[antibodies_well],
        wellplate_1_columns[:2],
        new_tip='never'
    )
    p50_multi.drop_tip()

    # 2. Aliquot 10 uL of PBS into columns 3-12 of plate 1
    p50_multi.pick_up_tip()
    p50_multi.distribute(
        PBS_volume,
        reservoir.wells()[PBS_well],
        wellplate_1_columns[2:12],
        new_tip='never', 
    )
    p50_multi.drop_tip()

    # 3. Serial dilution on columns 1, 3, 5, 7, 9, 11 and 2, 4, 6, 8, 10, 12, then discard extra in 11, 12
    for n in range(0, 2):
        for i in range(n, 10, 2):
            p50_multi.pick_up_tip()
            p50_multi.transfer(
                dilute_volume,
                wellplate_1_columns[i],
                wellplate_1_columns[i+2],
                mix_before=(mix_count, mix_volume),
                new_tip='never'
            )
            if i >= 8:
                p50_multi.transfer(
                    dilute_volume,
                    wellplate_1_columns[i+2],
                    reservoir.wells()[trash_well],
                    mix_before=(mix_count, mix_volume),
                    new_tip='never'
                )
            p50_multi.drop_tip()

    # 4. Add 10 uL of sporozoites into each well of plate 1
    p50_multi.pick_up_tip()
    p50_multi.distribute(
        sporozoites_volume,
        reservoir.wells()[sporozoites_well],
        wellplate_1_columns_reversed,
        new_tip='never'
    )
    p50_multi.drop_tip()

    # 5. Add 5 uL of FBS into each well of plate 1
    p50_multi.pick_up_tip()
    p50_multi.distribute(
        FBS_volume,
        reservoir.wells()[FBS_well],
        wellplate_1_columns_reversed,
        new_tip='never'
    )
    p50_multi.drop_tip()

        