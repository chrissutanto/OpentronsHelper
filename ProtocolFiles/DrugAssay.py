from opentrons import protocol_api

metadata = {
    'protocolName': 'Drug Assay',
    'author': 'Chris Sutanto',
    'description': 'Remove media and add liquid from a 12-well reservoir into a 96-well plate',
    'apiLevel': '2.2',
}

def run(protocol:protocol_api.ProtocolContext):

    # labware
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', '1')
    well_plate = protocol.load_labware('appliedbiosystems_96_wellplate_200ul', '2')
    tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', '7')

    # pipettes
    p300_multi = protocol.load_instrument('p300_multi', 'left', tip_racks = [tiprack])
    p50_multi = protocol.load_instrument('p50_multi', 'right')

    # modify
    source_well = 0 # Location of source in reservoir, 0-based indexing (left most well is 0)
    trash_well = 11 # Location of trash in reservoir, 0-based indexing (right most well is 11)
    remove_volume = 100 # Volume of media to remove from each well [uL]
    add_volume = 100 # Volume of liquid to add to each well [uL]
    aspiration_speed = 300 # Plunger speed while aspirating [mm/min]
    dispensation_speed = 500 # Plunger speed while dispensing [mm/min]
    # end modify

    # commands
    p300_multi.pick_up_tip()
    p300_multi.consolidate(
        remove_volume,
        well_plate.columns(),
        reservoir.wells()[trash_well],
        new_tip='never',
        aspirate_speed=aspiration_speed,
        dispense_speed=dispensation_speed)
    p300_multi.return_tip()

    p300_multi.pick_up_tip()
    p300_multi.distribute(
        add_volume,
        reservoir.wells()[source_well],
        well_plate.columns(),
        new_tip='never',
        aspirate_speed=aspiration_speed,
        dispense_speed=dispensation_speed,
        disposal_volume=3)
    p300_multi.return_tip()