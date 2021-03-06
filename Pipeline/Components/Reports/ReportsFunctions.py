from Pipeline.Tools import Tools as tools
import pickle
import json
import os



@tools.monitor_me()
def GetData(data_file_path):
    
    ''' Accepts data file path, returns object '''
    
    # initialize variables:
    data = None
    
    # check if file exists:
    if os.path.exists(data_file_path):
    
        with open(data_file_path, 'rb') as handle:
            data = pickle.load(handle)
    
    return data
    


@tools.monitor_me()
def BuildReportJson(file_paths, dicom_data, view_data, segmentation_data):
    
    ''' Accepts data as dictionaries, returns compiled json '''
    
    # drop unused key, values:
    if dicom_data is not None:
        del dicom_data['pixel_data']
    
    # drop unused key, values:    
    if segmentation_data is not None:
        del segmentation_data['pixel_data']
    
    # build report json:
    report_json = {
        'VISIT_DIR' : file_paths['VISIT_DIR'],
        'user_id' : file_paths['user_id'],
        'visit_id' : file_paths['visit_id'],
        'file_id' : file_paths['file_id'],
        'dicom_id' : file_paths['dicom_id'],
        'file_name' : file_paths['file_name'],
        'dicom' : dicom_data,
        'view' : view_data,
        'segmentation' : segmentation_data,
        'media' : {
            'dicom_mp4' : file_paths['dicom_mp4'],
            'segmentation_mp4' : file_paths['segmentation_mp4'],
            'simpsons_mp4' : file_paths['simpsons_mp4'],
            'dicom_webm' : file_paths['dicom_webm'],
            'segmentation_webm' : file_paths['segmentation_webm'],
            'simpsons_webm' : file_paths['simpsons_webm'],
        },
        'reports' : {
            'log' : file_paths['log_file'],
        }
    }
    
    return report_json
    
    

@tools.monitor_me()
def ExportReportJson(report_json, report_destination):
    
    ''' Accepts report_json, root destination, saves report_json as json in destination '''
    
    with open(report_destination, 'w') as json_file:
        json.dump(report_json, json_file)