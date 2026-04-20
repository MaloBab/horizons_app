import { ref } from 'vue'

const CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME as string
const UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET as string

export interface UploadResult {
  url: string
  publicId: string
}

export function useCloudinary() {
  const isUploading = ref(false)
  const uploadError = ref<string | null>(null)
  const uploadProgress = ref(0)

  async function uploadImage(file: File): Promise<UploadResult | null> {
    isUploading.value = true
    uploadError.value = null
    uploadProgress.value = 0

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('upload_preset', UPLOAD_PRESET)
      formData.append('folder', 'horizons/avatars')
      const result = await new Promise<UploadResult>((resolve, reject) => {
        const xhr = new XMLHttpRequest()

        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            uploadProgress.value = Math.round((e.loaded / e.total) * 100)
          }
        })

        xhr.addEventListener('load', () => {
          if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText)
            resolve({ url: data.secure_url, publicId: data.public_id })
          } else {
            reject(new Error("Échec de l'upload Cloudinary"))
          }
        })

        xhr.addEventListener('error', () => reject(new Error('Erreur réseau')))

        xhr.open('POST', `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`)
        xhr.send(formData)
      })

      return result
    } catch (err) {
      uploadError.value = err instanceof Error ? err.message : 'Erreur inconnue'
      return null
    } finally {
      isUploading.value = false
    }
  }

  return { uploadImage, isUploading, uploadError, uploadProgress }
}