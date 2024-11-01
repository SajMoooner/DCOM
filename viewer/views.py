from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pydicom
from PIL import Image
import numpy as np
import os


def home(request):
    if request.method == 'POST' and request.FILES.get('dicomFile'):
        dicom_file = request.FILES['dicomFile']
        file_path = default_storage.save('uploaded_dicom.dcm', ContentFile(dicom_file.read()))
        absolute_file_path = default_storage.path(file_path)

        # Načítaj DICOM súbor
        dicom_data = pydicom.dcmread(absolute_file_path)

        # Ulož všetky snímky ako samostatné obrázky
        img_paths = []
        if hasattr(dicom_data, 'NumberOfFrames') and dicom_data.NumberOfFrames > 1:
            for i in range(dicom_data.NumberOfFrames):
                pixel_array = dicom_data.pixel_array[i]
                normalized_array = (pixel_array / pixel_array.max()) * 255
                img_array = normalized_array.astype(np.uint8)
                img = Image.fromarray(img_array)
                img_path = os.path.join('media', f'dicom_image_{i}.png')
                img.save(img_path)
                img_paths.append(img_path)
        else:
            pixel_array = dicom_data.pixel_array
            normalized_array = (pixel_array / pixel_array.max()) * 255
            img_array = normalized_array.astype(np.uint8)
            img = Image.fromarray(img_array)
            img_path = os.path.join('media', 'dicom_image_0.png')
            img.save(img_path)
            img_paths.append(img_path)

        return render(request, 'viewer/index.html', {'num_frames': len(img_paths), 'img_paths': img_paths})

    return render(request, 'viewer/index.html')


def get_image_by_index(request, index):
    img_path = os.path.join('media', f'dicom_image_{index}.png')
    if os.path.exists(img_path):
        return JsonResponse({'img_url': '/' + img_path})
    return JsonResponse({'error': 'Image not found'}, status=404)
