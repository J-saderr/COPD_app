"use client";

import {
  ChangeEvent,
  FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type PredictionStatus = "pending" | "processing" | "completed" | "failed";

type PredictionLabel = "crackle" | "wheeze" | "both" | "none";

type Prediction = {
  id: string;
  filename: string;
  status: PredictionStatus;
  label?: PredictionLabel;
  confidence?: number;
  probabilities?: Record<PredictionLabel, number>;
  created_at?: string;
  updated_at?: string;
  notes?: string;
};

type UploadState = "idle" | "uploading" | "analyzing" | "complete" | "error";

const STATUS_THEME: Record<PredictionStatus, string> = {
  pending: "bg-amber-100 text-amber-800 ring-amber-200",
  processing: "bg-sky-100 text-sky-800 ring-sky-200",
  completed: "bg-emerald-100 text-emerald-800 ring-emerald-200",
  failed: "bg-rose-100 text-rose-800 ring-rose-200",
};

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [currentPrediction, setCurrentPrediction] = useState<Prediction | null>(
    null,
  );
  const [history, setHistory] = useState<Prediction[]>([]);
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const sortedHistory = useMemo(
    () =>
      [...history].sort(
        (a, b) =>
          new Date(b.created_at ?? 0).getTime() -
          new Date(a.created_at ?? 0).getTime(),
      ),
    [history],
  );

  const resetUpload = () => {
    setSelectedFile(null);
    setUploadState("idle");
    setErrorMessage(null);
  };

  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/audio?limit=10`, {
        next: { revalidate: 0 },
      });
      if (!response.ok) {
        throw new Error("Unable to load history");
      }
      const items: Prediction[] = await response.json();
      setHistory(items);
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files?.length) return;
    setSelectedFile(event.target.files[0]);
    setErrorMessage(null);
  };

  const pollPrediction = useCallback(async (predictionId: string) => {
    setUploadState("analyzing");
    for (let attempt = 0; attempt < 30; attempt += 1) {
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/audio/${predictionId}`,
        );
        if (!response.ok) {
          // Nếu là 404, có thể prediction chưa được tạo - tiếp tục retry
          if (response.status === 404 && attempt < 5) {
            await new Promise((resolve) => setTimeout(resolve, 1000));
            continue;
          }
          const errorText = await response.text();
          throw new Error(
            `Prediction lookup failed (${response.status}): ${
              errorText || "Unknown error"
            }`,
          );
        }
        const data: Prediction = await response.json();
        setCurrentPrediction(data);
        if (data.status === "completed" || data.status === "failed") {
          setHistory((prev) => {
            const other = prev.filter((item) => item.id !== data.id);
            return [data, ...other].slice(0, 10);
          });
          setUploadState(data.status === "completed" ? "complete" : "error");
          return;
        }
        await new Promise((resolve) => setTimeout(resolve, 2000));
      } catch (error) {
        // Nếu là network error và còn attempts, retry
        if (attempt < 5 && error instanceof TypeError) {
          await new Promise((resolve) => setTimeout(resolve, 1000));
          continue;
        }
        throw error;
      }
    }
    throw new Error("Prediction timed out");
  }, []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile) {
      setErrorMessage("Hãy chọn một file WAV/FLAC/MP3 trước khi tải lên.");
      return;
    }

    setUploadState("uploading");
    setErrorMessage(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/api/audio`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        let description = "Không thể tải lên âm thanh. Vui lòng thử lại.";
        if (response.status === 400) {
          description = "Định dạng file không hợp lệ.";
        } else if (response.status === 500) {
          description = "Lỗi server. Vui lòng kiểm tra backend.";
        }
        throw new Error(`${description} (${response.status}: ${errorText})`);
      }

      const predictionData: any = await response.json();
      
      // Handle both _id (from MongoDB) and id (from Pydantic)
      // Pydantic với Field(alias="_id") should convert to "id" in JSON
      const predictionId = predictionData?.id || predictionData?._id;
      
      if (!predictionData || !predictionId) {
        console.error("Invalid prediction response:", predictionData);
        throw new Error(
          `Server không trả về prediction ID hợp lệ. Response: ${JSON.stringify(predictionData)}`,
        );
      }
      
      const prediction: Prediction = {
        ...predictionData,
        id: predictionId,
      };
      
      setCurrentPrediction(prediction);
      await pollPrediction(prediction.id);
      await fetchHistory();
    } catch (error) {
      console.error("Upload error:", error);
      const message =
        error instanceof Error
          ? error.message
          : "Có lỗi xảy ra trong quá trình xử lý.";
      setErrorMessage(message);
      setUploadState("error");
    } finally {
      setSelectedFile(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <main className="mx-auto flex w-full max-w-5xl flex-col gap-10 px-6 py-12">
        <header className="space-y-2">
          <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            COPD AI Platform
          </p>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Phân tích âm phổi bằng AI
          </h1>
          <p className="max-w-2xl text-base text-slate-600">
            Tải lên bản ghi âm phổi (WAV, FLAC, MP3). Hệ thống sẽ dự đoán
            crackle, wheeze, both hoặc none với điểm tin cậy và lưu vào lịch sử
            để tiện theo dõi.
          </p>
        </header>

        <section className="grid gap-8 lg:grid-cols-3">
          <form
            onSubmit={handleSubmit}
            className="lg:col-span-2 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <h2 className="text-xl font-semibold text-slate-900">
              1. Tải lên âm phổi
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Hỗ trợ định dạng WAV, FLAC, MP3. Thời lượng tối ưu: 5-10 giây.
            </p>
            <div className="mt-6 flex flex-col gap-4">
              <label
                htmlFor="audio"
                className="flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-6 text-center transition hover:border-slate-400 hover:bg-slate-100"
              >
                <span className="text-sm font-medium text-slate-700">
                  {selectedFile
                    ? selectedFile.name
                    : "Chọn hoặc kéo thả file âm thanh"}
                </span>
                <span className="text-xs text-slate-500">
                  Dung lượng tối đa 10MB
                </span>
                <input
                  id="audio"
                  name="audio"
                  type="file"
                  accept="audio/*"
                  onChange={handleFileChange}
                  className="sr-only"
                />
              </label>

              <div className="flex items-center justify-between">
                <button
                  type="submit"
                  className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-indigo-300"
                  disabled={
                    uploadState === "uploading" || uploadState === "analyzing"
                  }
                >
                  {uploadState === "uploading"
                    ? "Đang tải lên..."
                    : uploadState === "analyzing"
                    ? "Đang phân tích..."
                    : "Phân tích ngay"}
                </button>
                <button
                  type="button"
                  onClick={resetUpload}
                  className="text-sm font-medium text-slate-500 hover:text-slate-700"
                  disabled={uploadState === "uploading"}
                >
                  Làm mới
                </button>
              </div>

              {errorMessage && (
                <p className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-600">
                  {errorMessage}
                </p>
              )}
            </div>
          </form>

          <aside className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-slate-900">
              2. Trạng thái hiện tại
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Hệ thống cập nhật kết quả tự động khi xử lý xong.
            </p>
            <div className="mt-4 space-y-4">
              {currentPrediction ? (
                <CurrentPredictionCard prediction={currentPrediction} />
              ) : (
                <p className="rounded-lg border border-dashed border-slate-200 px-4 py-6 text-sm text-slate-500">
                  Chưa có bản ghi nào đang phân tích.
                </p>
              )}
            </div>
          </aside>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-slate-900">
                3. Lịch sử gần đây
              </h2>
              <p className="text-sm text-slate-500">
                Lưu trữ 10 lượt phân tích gần nhất.
              </p>
            </div>
            <button
              type="button"
              onClick={fetchHistory}
              className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
            >
              Làm mới
            </button>
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {sortedHistory.length ? (
              sortedHistory.map((item, index) => (
                <PredictionCard key={item.id || `prediction-${index}`} item={item} />
              ))
            ) : (
              <p className="text-sm text-slate-500">
                Chưa có dữ liệu lịch sử nào.
              </p>
            )}
        </div>
        </section>
      </main>
    </div>
  );
}

function CurrentPredictionCard({ prediction }: { prediction: Prediction }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <header className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-500">File đang xử lý</p>
          <h3 className="text-base font-semibold text-slate-900">
            {prediction.filename}
          </h3>
        </div>
        <StatusBadge status={prediction.status} />
      </header>
      {prediction.status === "completed" && prediction.label && (
        <div className="mt-4 space-y-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">
              Kết quả chính
            </p>
            <p className="text-lg font-semibold text-slate-900">
              {labelToVietnamese(prediction.label)}
            </p>
            <p className="text-sm text-slate-500">
              Độ tin cậy:{" "}
              <span className="font-semibold">
                {formatPercentage(prediction.confidence)}
              </span>
            </p>
          </div>
          {prediction.probabilities && (
            <ProbabilityList probabilities={prediction.probabilities} />
          )}
        </div>
      )}
      {prediction.status === "failed" && (
        <p className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-600">
          {prediction.notes ?? "Không thể xử lý file âm thanh này."}
        </p>
      )}
    </div>
  );
}

function PredictionCard({ item }: { item: Prediction }) {
  return (
    <article className="rounded-xl border border-slate-200 p-4 shadow-sm transition hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="line-clamp-1 text-sm font-medium text-slate-900">
            {item.filename}
          </h3>
          <p className="text-xs text-slate-500">
            {item.created_at
              ? new Date(item.created_at).toLocaleString()
              : "—"}
          </p>
        </div>
        <StatusBadge status={item.status} />
      </div>

      {item.status === "completed" && item.label && (
        <div className="mt-3 space-y-2 text-sm text-slate-600">
          <p>
            Nhãn dự đoán:{" "}
            <span className="font-semibold text-slate-900">
              {labelToVietnamese(item.label)}
            </span>
          </p>
          <p>
            Độ tin cậy:{" "}
            <span className="font-semibold text-slate-900">
              {formatPercentage(item.confidence)}
            </span>
          </p>
          {item.probabilities && (
            <ProbabilityList probabilities={item.probabilities} />
          )}
        </div>
      )}

      {item.status === "failed" && (
        <p className="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-600">
          {item.notes ?? "Không thể xử lý file."}
        </p>
      )}
    </article>
  );
}

function ProbabilityList({
  probabilities,
}: {
  probabilities: Record<string, number>;
}) {
  return (
    <dl className="mt-2 grid grid-cols-2 gap-2 text-xs text-slate-500">
      {Object.entries(probabilities).map(([label, value]) => (
        <div key={label} className="rounded-lg bg-white px-3 py-2 shadow-inner">
          <dt className="uppercase tracking-wide text-slate-400">
            {labelToVietnamese(label as PredictionLabel)}
          </dt>
          <dd className="font-semibold text-slate-800">
            {formatPercentage(value)}
          </dd>
        </div>
      ))}
    </dl>
  );
}

function StatusBadge({ status }: { status: PredictionStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ring-1 ring-inset ${STATUS_THEME[status]}`}
    >
      {statusToVietnamese(status)}
    </span>
  );
}

function formatPercentage(value?: number) {
  if (typeof value !== "number") return "—";
  return `${(value * 100).toFixed(1)}%`;
}

function labelToVietnamese(label: PredictionLabel) {
  switch (label) {
    case "crackle":
      return "Crackle";
    case "wheeze":
      return "Wheeze";
    case "both":
      return "Crackle + Wheeze";
    case "none":
      return "Không phát hiện bất thường";
    default:
      return label;
  }
}

function statusToVietnamese(status: PredictionStatus) {
  switch (status) {
    case "pending":
      return "Đang chờ";
    case "processing":
      return "Đang xử lý";
    case "completed":
      return "Hoàn tất";
    case "failed":
      return "Lỗi";
    default:
      return status;
  }
}
