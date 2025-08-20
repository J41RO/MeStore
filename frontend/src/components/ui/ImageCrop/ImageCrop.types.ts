// src/components/ui/ImageCrop/ImageCrop.types.ts
import { Crop, PercentCrop } from 'react-image-crop';

export interface CropData {
  crop: Crop;
  croppedImageUrl: string;
  originalFile: File;
  croppedFile: File;
}

export interface ImageCropProps {
  imageFile: File;
  onCropComplete: (cropData: CropData) => void;
  onCancel: () => void;
  initialCrop?: PercentCrop;
  aspectRatio?: number;
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
  className?: string;
}

export interface CropResult {
  croppedImageUrl: string;
  croppedFile: File;
  crop: Crop;
}