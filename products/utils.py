from datetime import datetime

def Category_image_renamer(instance,filename):
    '''
    function to rename the category image with datetime
    '''
    
    timestamp = str(datetime.today())
    return f'category_Images/{timestamp}-{filename}'
    
