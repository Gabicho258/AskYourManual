import { useState } from "react";
import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import {
  FileText,
  Upload,
  Trash2,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
} from "lucide-react";
import {
  useDocuments,
  useUploadDocument,
  useDeleteDocument,
  useReprocessDocument,
} from "@/hooks";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import type { DocumentStatus } from "@/types";

export function DocumentsPage() {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadDescription, setUploadDescription] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const { data: documentsData, isLoading } = useDocuments();
  const uploadMutation = useUploadDocument();
  const deleteMutation = useDeleteDocument();
  const reprocessMutation = useReprocessDocument();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
      setShowUploadModal(true);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    multiple: false,
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      await uploadMutation.mutateAsync({
        file: selectedFile,
        title: uploadTitle || undefined,
        description: uploadDescription || undefined,
      });

      setShowUploadModal(false);
      setSelectedFile(null);
      setUploadTitle("");
      setUploadDescription("");
    } catch (error) {
      console.error("Error uploading:", error);
    }
  };

  const getStatusIcon = (status: DocumentStatus) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-red-600" />;
      case "processing":
        return <Clock className="h-5 w-5 text-yellow-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: DocumentStatus) => {
    const variants = {
      completed: "success" as const,
      failed: "error" as const,
      processing: "warning" as const,
      pending: "default" as const,
    };
    return variants[status] || "default";
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documentos</h1>
          <p className="text-gray-600">
            Gestiona los manuales Komatsu en el sistema
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-600">
            {documentsData?.total || 0} documentos
          </span>
        </div>
      </div>

      {/* Zona de carga */}
      <Card>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-primary-500 bg-primary-50"
              : "border-gray-300 hover:border-gray-400"
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {isDragActive ? "Suelta el archivo aquí" : "Subir nuevo documento"}
          </h3>
          <p className="text-gray-600">
            Arrastra un archivo PDF o haz clic para seleccionar
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Solo archivos PDF, máximo 50MB
          </p>
        </div>
      </Card>

      {/* Lista de documentos */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {documentsData?.documents.map((doc) => (
          <Card key={doc.id} className="relative">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                {getStatusIcon(doc.status)}
                <h3 className="font-medium text-gray-900 truncate">
                  {doc.title || doc.filename}
                </h3>
              </div>
              <Badge variant={getStatusBadge(doc.status)} size="sm">
                {doc.status}
              </Badge>
            </div>

            <div className="space-y-2 text-sm text-gray-600 mb-4">
              <p>
                <strong>Archivo:</strong> {doc.filename}
              </p>
              <p>
                <strong>Tamaño:</strong> {formatFileSize(doc.file_size)}
              </p>
              <p>
                <strong>Chunks:</strong> {doc.chunk_count}
              </p>
              <p>
                <strong>Creado:</strong>{" "}
                {formatDistanceToNow(new Date(doc.created_at), {
                  addSuffix: true,
                  locale: es,
                })}
              </p>
              {doc.processing_time && (
                <p>
                  <strong>Tiempo proc.:</strong>{" "}
                  {doc.processing_time.toFixed(2)}s
                </p>
              )}
            </div>

            {doc.description && (
              <p className="text-sm text-gray-700 mb-4 italic">
                {doc.description}
              </p>
            )}

            {doc.error_message && (
              <div className="bg-red-50 border border-red-200 rounded p-2 mb-4">
                <p className="text-sm text-red-700">{doc.error_message}</p>
              </div>
            )}

            <div className="flex items-center justify-between">
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => reprocessMutation.mutate(doc.filename)}
                  disabled={reprocessMutation.isPending}
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => deleteMutation.mutate(doc.filename)}
                  disabled={deleteMutation.isPending}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Modal de carga */}
      <Modal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        title="Subir documento"
        size="md"
      >
        <div className="space-y-4">
          {selectedFile && (
            <div className="bg-gray-50 rounded p-3">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-gray-600" />
                <span className="font-medium">{selectedFile.name}</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
          )}

          <Input
            label="Título (opcional)"
            value={uploadTitle}
            onChange={(e) => setUploadTitle(e.target.value)}
            placeholder="Ej: Manual de operación D65EX"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción (opcional)
            </label>
            <textarea
              value={uploadDescription}
              onChange={(e) => setUploadDescription(e.target.value)}
              placeholder="Describe el contenido del manual..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md resize-none"
              rows={3}
            />
          </div>

          <div className="flex justify-end space-x-3">
            <Button variant="outline" onClick={() => setShowUploadModal(false)}>
              Cancelar
            </Button>
            <Button onClick={handleUpload} loading={uploadMutation.isPending}>
              Subir documento
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
