import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Camera } from 'lucide-react'

interface ImageUploadProps {
  onImagesSelected: (images: string[]) => void
}

const ImageUpload = ({ onImagesSelected }: ImageUploadProps) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const imagePromises = acceptedFiles.map(file => {
      return new Promise<string>((resolve) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          resolve(e.target?.result as string)
        }
        reader.readAsDataURL(file)
      })
    })

    Promise.all(imagePromises).then((images) => {
      onImagesSelected(images)
    })
  }, [onImagesSelected])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    multiple: true,
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  return (
    <div
      {...getRootProps()}
      className={`
        relative cursor-pointer border-2 border-dashed rounded-xl p-4 transition-all duration-200
        ${isDragActive && !isDragReject
          ? 'border-pink-500 bg-pink-50' 
          : isDragReject
          ? 'border-red-500 bg-red-50'
          : 'border-gray-300 hover:border-pink-400 hover:bg-pink-25'
        }
      `}
    >
      <input {...getInputProps()} />
      
      <div className="flex flex-col items-center space-y-2 text-center">
        {isDragActive ? (
          <>
            <Camera className="w-8 h-8 text-pink-500" />
            <div className="text-sm text-pink-600 font-medium">
              {isDragReject ? 'Please upload valid image files' : 'Drop images here!'}
            </div>
          </>
        ) : (
          <>
            <Upload className="w-8 h-8 text-gray-400" />
            <div className="text-sm text-gray-600">
              <span className="font-medium text-pink-600">Upload photos</span>
              <br />
              <span className="text-xs">or drag & drop</span>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default ImageUpload
