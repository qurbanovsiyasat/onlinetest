export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Yükleniyor...</h2>
        <p className="text-gray-600">Squiz Platform hazırlanıyor</p>
      </div>
    </div>
  )
}
