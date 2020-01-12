from Pipeline.Tools import Tools as tools
from decouple import config
import numpy as np
import subprocess
import pydicom 
import pickle
import boto3
import sys
import cv2
import os



# manufacturer groups:
global manufacturer_groups
manufacturer_groups = {
    1 : [
        'Acuson Cypress',           'GE Healthcare LOGIQe',     'GE Healthcare Ultrasound Vivid iq',    
        'GE Healthcare Vivid i',    'GE Healthcare Vivide',     'GEMS Ultrasound Vivid i',      
        'MINDRAY M7',               'SIEMENS ACUSON P500',      'Teratech Corp. Terason Ultrasound Imaging System',
        'Acuson',                   None,
    ],
    2 : [
        'Sonoscanner',
    ],
    3 : [
        'Unknown',
    ],
}



@tools.monitor_me()
def DownloadFileFromS3(s3_file_path, destination_directory):

    ''' Accepts file_path of dicom file in s3 bucket, downloads file locally for processing '''

    # get bucket name:
    BUCKET_NAME = config('AWS_S3_BUCKET_NAME')
    
    # set up client:
    client = boto3.client('s3', aws_access_key_id=config('AWS_ACCESS_KEY_ID'), aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
    s3 = boto3.resource('s3')

    # build file destintation:
    file_destination = destination_directory + s3_file_path

    # download file:
    s3.Bucket(BUCKET_NAME).download_file('staging/' + s3_file_path, file_destination)

    # delete file from s3 staging folder:
    #s3.Bucket(BUCKET_NAME).delete_objects(Delete={'Objects' : [ { 'Key' : s3_file_path, }]})

    return file_destination



@tools.monitor_me()
def ReadDicomFile(dicom_file_path):
    
    ''' Accepts dicom file path (hashed s3_key), returns dicom raises ERROR if file is not a dicom ".dcm" file '''
    
    # try extracting as dicom file:
    try:
        
        dicom = pydicom.dcmread(dicom_file_path)
        
    # otherwise try extracting as .mov or .mp4 file:
    except:
        
        # instantiate dicom with data from video:    
        dicom = Dicom(dicom_file_path)
        
    # # if dicom file, extract using pydicom library:
    # if file_name[-3:] == 'dcm':
        
    #     dicom = pydicom.dcmread(dicom_file_path)
        
    # # if .mov or .mp4 file, create mock dicom object:
    # elif file_name[-3:] == 'mov' or file_name[-3:] == 'mp4':
        
    #     # instantiate dicom with data from video:    
    #     dicom = Dicom(dicom_file_path)
        
    return dicom



@tools.monitor_me()
def GetManufacturerDetails(dicom):
    
    ''' Accepts a dicom object, returns manufacturer detials '''
    
    # initialize variables:
    manufacturer_details = {
        'manufacturer' : None,
        'manufacturer_model_name' : None,
    } 
    
    if dicom.Manufacturer in manufacturer_groups[1]:
    
        manufacturer_details['manufacturer'] = dicom.Manufacturer 
        manufacturer_details['manufacturer_model_name'] = dicom.ManufacturerModelName
        
    elif dicom.Manufacturer in manufacturer_groups[2]:
        
        manufacturer_details['manufacturer'] = dicom.Manufacturer 
        
    elif dicom.Manufacturer in manufacturer_groups[3]:
        
        manufacturer_details['manufacturer'] = dicom.Manufacturer
        
    return manufacturer_details
    
    
    
@tools.monitor_me()
def GetImageSizeDetails(dicom):
    
    ''' Accepts dicom object, returns image size details '''
    
    # intialize variables:
    image_size_details = {
        'physical_delta_x' : None,
        'physical_delta_y' : None,
        'physical_units_x_direction' : None,
        'physical_units_y_direction' : None,
    }
    
    if dicom.Manufacturer in manufacturer_groups[1]:
    
        image_size_details['physical_units_x_direction'] = dicom.SequenceOfUltrasoundRegions[0].PhysicalUnitsXDirection
        image_size_details['physical_units_y_direction'] = dicom.SequenceOfUltrasoundRegions[0].PhysicalUnitsYDirection
        image_size_details['physical_delta_x'] = abs(dicom.SequenceOfUltrasoundRegions[0].PhysicalDeltaX)
        image_size_details['physical_delta_y'] = abs(dicom.SequenceOfUltrasoundRegions[0].PhysicalDeltaY)
        
    elif dicom.Manufacturer in manufacturer_groups[2]:
        
        image_size_details['physical_units_x_direction'] = dicom.PhysicalUnitsXDirection
        image_size_details['physical_units_y_direction'] = dicom.PhysicalUnitsYDirection
        image_size_details['physical_delta_x'] = abs(dicom.PhysicalDeltaX)
        image_size_details['physical_delta_y'] = abs(dicom.PhysicalDeltaY)
        
    elif dicom.Manufacturer in manufacturer_groups[3]:
        pass
            
    return image_size_details
    
    

@tools.monitor_me()
def GetDicomTypeDetails(dicom):
    
    ''' Accepts dicom object, returns dicom type '''
    
    # initilaize varibles:
    dicom_type_details = None
    
    if dicom.Manufacturer in manufacturer_groups[1]: 
        
        if dicom.SequenceOfUltrasoundRegions[0].RegionDataType == 1:
            dicom_type_details = 'standard'
        elif dicom.SequenceOfUltrasoundRegions[0].RegionDataType == 2:
            dicom_type_details = 'color'
    
    elif dicom.Manufacturer in manufacturer_groups[2]:
    
        if (dicom.RegionDataType == 1) or (dicom.RegionDataType == 0):
            dicom_type_details = 'standard'
        elif dicom.RegionDataType == 2:
            dicom_type_details = 'color' 
    
    elif dicom.Manufacturer in manufacturer_groups[3]:
        pass
    
    return dicom_type_details
    
    
    
@tools.monitor_me()
def GetNumberOfFramesDetails(dicom):
    
    ''' Accepts dicom object, returns number of frames in dicom '''
    
    # initialize variables:
    number_of_frames_details = None
    
    number_of_frames_details = dicom.NumberOfFrames
        
    return number_of_frames_details
    
    
    
@tools.monitor_me()
def GetFrameTimeDetails(dicom):
    
    ''' Accepts dicom object, returns seconds per frame in dicom '''
    
    # initialize variables:
    seconds_per_frame = None
    
    seconds_per_frame = dicom.FrameTime
    seconds_per_frame = float(seconds_per_frame)/1000
        
    return seconds_per_frame
    


@tools.monitor_me()
def GetPixelArrayDataDetails(dicom):
    
    ''' Accepts dicom object, returns pixel array data details '''
    
    # intialize variables:
    pixel_array_data_details = None
    
    pixel_array_data_details = dicom.pixel_array
    
    return pixel_array_data_details
    
    

@tools.monitor_me(save_output=True)
def CompileDicomDetails(dicom_id, manufacturer_details, image_size_details, dicom_type_details, number_of_frames_details, frame_time_details, pixel_data_details):
    
    ''' Accepts dicom details, returns compiled dicom object '''
    
    dicom = {
        'dicom_id' : dicom_id,
        'manufacturer' : manufacturer_details['manufacturer'],
        'manufacturer_model_name' : manufacturer_details['manufacturer_model_name'],
        'physical_units_x_direction' : image_size_details['physical_units_x_direction'],
        'physical_units_y_direction' : image_size_details['physical_units_y_direction'],
        'physical_delta_x' : image_size_details['physical_delta_x'],
        'physical_delta_y' : image_size_details['physical_delta_y'],
        'dicom_type' : dicom_type_details,
        'number_of_frames' : number_of_frames_details,
        'seconds_per_frame' : frame_time_details,
        'pixel_data' : pixel_data_details,
    }
    
    return dicom
    
    
    
@tools.monitor_me()
def ExportDicom(dicom, destination):
    
    ''' Accepts dicom, saves data in .pkl format '''
    
    with open(destination, 'wb') as handle:
        pickle.dump(dicom, handle)



# create mock dicom object:
class Dicom:

    ''' Mock dicom object created from .mov or .mp4 files '''

    def __init__(self, path_to_non_dicom_file):
        
        raw_video = cv2.VideoCapture(path_to_non_dicom_file)

        # get numpy shape from video:
        frame_count = int(raw_video.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_height = int(raw_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_width = int(raw_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        
        # initialize pixel data array:
        pixel_data = np.empty((frame_count, frame_height, frame_width, 3), np.dtype('uint8'))
        
        counter = 0
        extraction_success = True
        
        # extract each frame:
        while (counter < frame_count and extraction_success):
            extraction_success, pixel_data[counter] = raw_video.read()
            counter += 1
        
        # get number of frames:
        number_of_frames = pixel_data.shape[0]
        
        # get frame_time (milliseconds per frame):
        frame_time = 1000 / raw_video.get(cv2.CAP_PROP_FPS) 
        
        # limit frame count to first 150 frames:
        if pixel_data.shape[0] > 150:
            pixel_data = pixel_data[0:150]
            
            frame_time *= 150/pixel_data.shape[0]
        
        # create dicom fields for extraction:
        self.pixel_array = pixel_data
        self.NumberOfFrames = number_of_frames
        self.FrameTime = frame_time
        self.Manufacturer = 'Unknown'

    
    