from opentrons import protocol_api

metadata = {
    'protocolName': 'RTPCR',
    'author': 'Chris Sutanto',
    'description': 'RTPCR',
    'apiLevel': '2.2',
    'modify': 'True',
    'well-map': 'True'
}

def run(protocol:protocol_api.ProtocolContext):

    # modify
    source_1_volume = 1 # Volume of master mix to distribute into each well
    source_2_volume = 1 # Volume of cDNA sample to distribute into each well
    # end modify

    # labware
    single_tiprack = protocol.load_labware(
        'opentrons_96_tiprack_300ul', '1') # 300 uL tips 

    multi_tiprack = protocol.load_labware(
        'opentrons_96_tiprack_300ul', '2') # 300 uL tips 

    source_1 = protocol.load_labware(
        'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '6') # master mix in 1.5 mL tube rack

    source_2 = protocol.load_labware(
        'biorad_96_wellplate_200ul_pcr', '3') # placeholder for 8-tube strip holder containing cDNA samples

    destination = protocol.load_labware(
        'biorad_96_wellplate_200ul_pcr', '5') # 96 well plate
    

    # pipettes
    single_pipette = protocol.load_instrument(
        'p300_single', 'left', tip_racks = [single_tiprack])
    
    multi_pipette = protocol.load_instrument(
        'p300_multi', 'right', tip_racks = [multi_tiprack])

    # commands

