UPDATE 
    ManuallyAddedViewsData
SET 
    in_use = true,
    previous_object_id = '{previous_object_id}'
WHERE 
    object_id = '{object_id}';