import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  activateCalendarByCrop,
  createEnvironmental,
  createIrrigation,
  createCrop,
  deleteCrop,
  getMyCrops,
  updateCrop,
  updateEnvironmental,
  updateIrrigation,
  upsertCalendarByCrop,
} from "../api/api";
import CropTasks from "../components/CropTasks";
import { translateWateringFrequency, translateSunExposure } from "../utils/translations";
import { defaultCropImage, resolveCropImageSrc } from "../utils/cropImages";

const parseJwt = (token) => {
  try {
    const payload = token.split(".")[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decoded);
  } catch {
    return null;
  }
};

const leftArrowIcon =
  "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NCA2NCI+PHBhdGggZD0iTTQyIDEyIEwyMiAzMiBMNDIgNTIiIHN0cm9rZT0iIzI3NjMzRSIgc3Ryb2tlLXdpZHRoPSIxMCIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+";
const rightArrowIcon =
  "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NCA2NCI+PHBhdGggZD0iTTIyIDEyIEw0MiAzMiBMMjIgNTIiIHN0cm9rZT0iIzI3NjMzRSIgc3Ryb2tlLXdpZHRoPSIxMCIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+";

const PAGE_SIZE = 12;
const toDateInputValue = (value) => (value ? String(value).slice(0, 10) : "");
const nullableDate = (value) => value || null;
const monthsOptions = [
  "Enero",
  "Febrero",
  "Marzo",
  "Abril",
  "Mayo",
  "Junio",
  "Julio",
  "Agosto",
  "Septiembre",
  "Octubre",
  "Noviembre",
  "Diciembre",
];

const phaseDateFromMonthHalf = (month, half) => {
  if (!month || !half) return "";
  const day = half === "1" ? "01" : "16";
  return `2000-${String(month).padStart(2, "0")}-${day}`;
};

const monthFromPhaseDate = (value) => {
  const date = toDateInputValue(value);
  return date ? String(Number(date.slice(5, 7))) : "";
};

const halfFromPhaseDate = (value) => {
  const date = toDateInputValue(value);
  if (!date) return "";
  return Number(date.slice(8, 10)) <= 15 ? "1" : "2";
};

const PhaseSelectors = ({ label, value, onChange }) => (
  <>
    <div style={formField}>
      <label style={labelStyle}>{label} - mes</label>
      <select
        value={monthFromPhaseDate(value)}
        onChange={(event) => onChange(phaseDateFromMonthHalf(event.target.value, halfFromPhaseDate(value) || "1"))}
        style={inputStyle}
      >
        <option value="">Selecciona mes</option>
        {monthsOptions.map((month, index) => (
          <option key={month} value={String(index + 1)}>
            {month}
          </option>
        ))}
      </select>
    </div>
    <div style={formField}>
      <label style={labelStyle}>{label} - quincena</label>
      <select
        value={halfFromPhaseDate(value)}
        onChange={(event) => onChange(phaseDateFromMonthHalf(monthFromPhaseDate(value), event.target.value))}
        style={inputStyle}
      >
        <option value="">Selecciona quincena</option>
        <option value="1">Primera quincena</option>
        <option value="2">Segunda quincena</option>
      </select>
    </div>
  </>
);

export default function Crops({ token }) {
  const navigate = useNavigate();
  const [crops, setCrops] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: PAGE_SIZE,
    total_pages: 1,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editMode, setEditMode] = useState(false);

  const [name, setName] = useState("");
  const [type, setType] = useState("");
  const [lifeCycle, setLifeCycle] = useState("anual");
  const [isPublic, setIsPublic] = useState(false);
  const [saving, setSaving] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const fileInputRef = useRef(null);

  const [wateringFrequency, setWateringFrequency] = useState("daily");
  const [waterAmount, setWaterAmount] = useState("");
  const [irrigationRecommendations, setIrrigationRecommendations] = useState("");
  const [sunExposure, setSunExposure] = useState("full_sun");
  const [minTemp, setMinTemp] = useState("");
  const [maxTemp, setMaxTemp] = useState("");
  const [frostTolerance, setFrostTolerance] = useState(false);
  const [plantingStart, setPlantingStart] = useState("");
  const [transplantStart, setTransplantStart] = useState("");
  const [harvestStart, setHarvestStart] = useState("");

  const currentUser = useMemo(() => parseJwt(token), [token]);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setImageFile(file);

    if (file) {
      setPreviewUrl(URL.createObjectURL(file));
    } else {
      setPreviewUrl(null);
    }
  };

  const loadCrops = useCallback(async (requestedPage = currentPage, options = {}) => {
    setLoading(true);
    setError(null);
    if (options.clearMessage !== false) {
      setMessage(null);
    }

    try {
      const data = await getMyCrops(token, {
        page: requestedPage,
        page_size: PAGE_SIZE,
      });

      setCrops(data.items || []);
      setPagination({
        total: data.total || 0,
        page: data.page || 1,
        page_size: data.page_size || PAGE_SIZE,
        total_pages: data.total_pages || 1,
      });
    } catch (err) {
      setError(err.message || "Error cargando cultivos");
    } finally {
      setLoading(false);
    }
  }, [currentPage, token]);

  const handleCreateCrop = async () => {
    if (!name.trim() || !type.trim() || !lifeCycle) {
      setError("Nombre, tipo y ciclo de vida son obligatorios");
      return;
    }

    if (!currentUser?.user_id) {
      setError("No se pudo leer el usuario del token");
      return;
    }

    setSaving(true);
    setError(null);
    setMessage(null);

    try {
      const cropData = new FormData();
      cropData.append("name", name.trim());
      cropData.append("type", type.trim());
      cropData.append("life_cycle", lifeCycle);
      cropData.append("user_id", String(currentUser.user_id));
      cropData.append("is_public", String(currentUser?.role === "admin" && isPublic));

      if (imageFile) {
        cropData.append("image", imageFile);
      }

      await createCrop(token, cropData);

      if (wateringFrequency !== "daily" || waterAmount || irrigationRecommendations ||
          sunExposure !== "full_sun" || minTemp || maxTemp || frostTolerance) {
      }

      resetForm();

      setMessage("Cultivo creado correctamente");
      setShowCreateModal(false);
      setCurrentPage(1);
      await loadCrops(1);
    } catch (err) {
      setError(err.message || "No se pudo crear el cultivo");
    } finally {
      setSaving(false);
    }
  };

  const resetForm = () => {
    setName("");
    setType("");
    setLifeCycle("anual");
    setIsPublic(false);
    setImageFile(null);

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setPreviewUrl(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }

    setWateringFrequency("daily");
    setWaterAmount("");
    setIrrigationRecommendations("");
    setSunExposure("full_sun");
    setMinTemp("");
    setMaxTemp("");
    setFrostTolerance(false);
    setPlantingStart("");
    setTransplantStart("");
    setHarvestStart("");
  };

  useEffect(() => {
    loadCrops();
  }, [loadCrops]);

  const loadCropIntoEditForm = (crop) => {
    setName(crop.name || "");
    setType(crop.type || "");
    setLifeCycle(crop.life_cycle || "anual");
    setIsPublic(Boolean(crop.is_public));

    setWateringFrequency(crop.irrigation?.watering_frequency || "daily");
    setWaterAmount(crop.irrigation?.water_amount ?? "");
    setIrrigationRecommendations(crop.irrigation?.recommendations || "");

    setSunExposure(crop.environmental?.sun_exposure || "full_sun");
    setMinTemp(crop.environmental?.min_temp ?? "");
    setMaxTemp(crop.environmental?.max_temp ?? "");
    setFrostTolerance(Boolean(crop.environmental?.frost_tolerance));

    setPlantingStart(toDateInputValue(crop.calendar?.planting_start));
    setTransplantStart(toDateInputValue(crop.calendar?.transplant_start));
    setHarvestStart(toDateInputValue(crop.calendar?.harvest_start));
  };

  const beginEditCrop = () => {
    if (!selectedCrop) return;
    loadCropIntoEditForm(selectedCrop);
    setEditMode(true);
    setError(null);
    setMessage(null);
  };

  const upsertRelatedData = async (cropId) => {
    const irrigationData = {
      crop_id: cropId,
      watering_frequency: wateringFrequency,
      water_amount: Number(waterAmount || 0),
      recommendations: irrigationRecommendations,
    };

    const environmentalData = {
      crop_id: cropId,
      sun_exposure: sunExposure,
      min_temp: Number(minTemp || 0),
      max_temp: Number(maxTemp || 0),
      frost_tolerance: frostTolerance,
    };

    const calendarData = {
      planting_start: nullableDate(plantingStart),
      planting_end: nullableDate(plantingStart),
      transplant_start: nullableDate(transplantStart),
      transplant_end: nullableDate(transplantStart),
      harvest_start: nullableDate(harvestStart),
      harvest_end: nullableDate(harvestStart),
    };

    const irrigation = selectedCrop.irrigation?.id
      ? await updateIrrigation(token, selectedCrop.irrigation.id, irrigationData)
      : await createIrrigation(token, irrigationData);

    const environmental = selectedCrop.environmental?.id
      ? await updateEnvironmental(token, selectedCrop.environmental.id, environmentalData)
      : await createEnvironmental(token, environmentalData);

    const calendar = await upsertCalendarByCrop(token, cropId, calendarData);

    return { irrigation, environmental, calendar };
  };

  const handleSaveCropDetails = async () => {
    if (!selectedCrop) return;
    if (!name.trim() || !type.trim() || !lifeCycle) {
      setError("Nombre, tipo y ciclo de vida son obligatorios");
      return;
    }

    setSaving(true);
    setError(null);
    setMessage(null);

    try {
      const updated = await updateCrop(token, selectedCrop.id, {
        name: name.trim(),
        type: type.trim(),
        life_cycle: lifeCycle,
        image_url: selectedCrop.image_url,
        user_id: selectedCrop.user_id,
        is_public: selectedCrop.is_public,
        source_crop_id: selectedCrop.source_crop_id,
      });

      const related = await upsertRelatedData(selectedCrop.id);
      const nextCrop = { ...updated, ...related };

      setCrops((prev) => prev.map((crop) => (crop.id === nextCrop.id ? nextCrop : crop)));
      setSelectedCrop(nextCrop);
      setEditMode(false);
      setMessage("Cultivo actualizado correctamente");
    } catch (err) {
      setError(err.message || "No se pudo actualizar el cultivo");
    } finally {
      setSaving(false);
    }
  };

  const handleActivateCalendar = async () => {
    if (!selectedCrop) return;

    setSaving(true);
    setError(null);
    setMessage(null);

    try {
      const calendar = await activateCalendarByCrop(token, selectedCrop.id);
      const nextCrop = { ...selectedCrop, calendar };
      setCrops((prev) => prev.map((crop) => (crop.id === nextCrop.id ? nextCrop : crop)));
      setSelectedCrop(nextCrop);
      setMessage("Cultivo añadido al calendario correctamente");
    } catch (err) {
      setError(err.message || "Completa las quincenas de siembra, trasplante y cosecha antes de añadir este cultivo al calendario");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteCrop = async () => {
    if (!selectedCrop) return;

    const confirmed = window.confirm(`¿Quitar "${selectedCrop.name}" de mis cultivos?`);
    if (!confirmed) return;

    setSaving(true);
    setError(null);
    setMessage(null);

    try {
      await deleteCrop(token, selectedCrop.id);

      const nextPage = crops.length === 1 && currentPage > 1
        ? currentPage - 1
        : currentPage;

      setShowModal(false);
      setSelectedCrop(null);
      setEditMode(false);
      resetForm();

      if (nextPage !== currentPage) {
        setCurrentPage(nextPage);
      } else {
        await loadCrops(nextPage, { clearMessage: false });
      }

      setMessage("Cultivo quitado de mis cultivos correctamente");
    } catch (err) {
      setError(err.message || "No se pudo quitar el cultivo de mis cultivos");
    } finally {
      setSaving(false);
    }
  };

  const handleImageError = (event) => {
    event.currentTarget.onerror = null;
    event.currentTarget.src = defaultCropImage;
  };

  const selectedIndex = selectedCrop
    ? crops.findIndex((crop) => crop.id === selectedCrop.id)
    : -1;

  const prevCrop = selectedIndex > 0 ? crops[selectedIndex - 1] : null;
  const nextCrop = selectedIndex >= 0 && selectedIndex < crops.length - 1
    ? crops[selectedIndex + 1]
    : null;

  const goToPrevCrop = () => {
    if (prevCrop) {
      setSelectedCrop(prevCrop);
    }
  };

  const goToNextCrop = () => {
    if (nextCrop) {
      setSelectedCrop(nextCrop);
    }
  };

  if (loading) return <p style={{ padding: "20px" }}>⏳ Cargando cultivos...</p>;

  return (
    <>
      <style>{`
        .crop-modal-content {
          scrollbar-width: thin;
          scrollbar-color: #3B8242 rgba(255, 255, 255, 0.75);
        }

        .crop-modal-content::-webkit-scrollbar {
          width: 10px;
          height: 10px;
        }

        .crop-modal-content::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.75);
          border-radius: 999px;
        }

        .crop-modal-content::-webkit-scrollbar-thumb {
          background: #3B8242;
          border-radius: 999px;
          border: 2px solid rgba(255, 255, 255, 0.9);
          background-clip: padding-box;
        }

        .crop-modal-content::-webkit-scrollbar-thumb:hover {
          background: #2F6B33;
        }
      `}</style>
      <div style={page}>
        <header style={headerStyle}>
        <div>
          <h1 style={titleStyle}>🌿 Mis cultivos</h1>
          <p style={subtitleStyle}>
            Explora tus plantaciones con imágenes y datos clave en un diseño claro.
          </p>
        </div>
        <div style={{ display: "flex", gap: "12px" }}>
          <button 
            style={primaryButton} 
            onClick={() => {
              setShowCreateModal(true);
              setError(null);
              setMessage(null);
            }}
          >
            ➕ Añadir cultivo
          </button>
          <button style={secondaryButton} onClick={() => loadCrops()}>
            🔄 Actualizar
          </button>
        </div>
      </header>

      {message && <p style={statusSuccess}>{message}</p>}
      {error && <p style={statusError}>{error}</p>}

      {showCreateModal && (
        <div style={modalOverlay}>
          <div className="crop-modal-content" style={createModalContent}>
            <div style={modalHeader}>
              <h2 style={modalTitle}>🌱 Añadir nuevo cultivo</h2>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  resetForm();
                  setError(null);
                  setMessage(null);
                }}
                style={closeButton}
              >
                ✕
              </button>
            </div>

            <div style={modalBody}>
              {error && <p style={statusError}>{error}</p>}

              <div style={formSection}>
                <h3 style={sectionTitle}>Información básica</h3>
                <div style={formGrid}>
                  <div style={formField}>
                    <label style={labelStyle}>
                      Nombre <span style={{ color: "#ef4444" }}>*</span>
                    </label>
                    <input
                      placeholder="Ej: Tomate cherry"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      style={inputStyle}
                      required
                    />
                  </div>

                  <div style={formField}>
                    <label style={labelStyle}>
                      Tipo <span style={{ color: "#ef4444" }}>*</span>
                    </label>
                    <input
                      placeholder="Ej: Hortaliza, Cereal, Aromática"
                      value={type}
                      onChange={(e) => setType(e.target.value)}
                      style={inputStyle}
                      required
                    />
                  </div>

                  <div style={formField}>
                    <label style={labelStyle}>
                      Ciclo de vida <span style={{ color: "#ef4444" }}>*</span>
                    </label>
                    <select
                      value={lifeCycle}
                      onChange={(e) => setLifeCycle(e.target.value)}
                      style={inputStyle}
                      required
                    >
                      <option value="anual">Anual</option>
                      <option value="bienal">Bienal</option>
                      <option value="perenne">Perenne</option>
                    </select>
                  </div>

                  {currentUser?.role === "admin" && (
                    <div style={formField}>
                      <label style={{ ...labelStyle, display: "flex", alignItems: "center", gap: "8px" }}>
                        <input
                          type="checkbox"
                          checked={isPublic}
                          onChange={(e) => setIsPublic(e.target.checked)}
                          style={{ width: "16px", height: "16px" }}
                        />
                        Publicar en catalogo
                      </label>
                    </div>
                  )}

                  <div style={formField}>
                    <label style={labelStyle}>Imagen (opcional)</label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      ref={fileInputRef}
                      style={inputStyle}
                    />
                  </div>
                </div>

                {previewUrl && (
                  <div style={previewWrapper}>
                    <p style={previewLabel}>Vista previa de la imagen</p>
                    <img
                      src={previewUrl}
                      alt="Vista previa del cultivo"
                      style={previewImage}
                    />
                  </div>
                )}
              </div>

              <div style={formSection}>
                <h3 style={sectionTitle}>💧 Información de riego (opcional)</h3>
                <div style={formGrid}>
                  <div style={formField}>
                    <label style={labelStyle}>Frecuencia de riego</label>
                    <select
                      value={wateringFrequency}
                      onChange={(e) => setWateringFrequency(e.target.value)}
                      style={inputStyle}
                    >
                      <option value="daily">Diario</option>
                      <option value="2 times/week">2 veces por semana</option>
                      <option value="3 times/week">3 veces por semana</option>
                      <option value="weekly">Semanal</option>
                    </select>
                  </div>

                  <div style={formField}>
                    <label style={labelStyle}>Cantidad de agua (litros)</label>
                    <input
                      type="number"
                      step="0.1"
                      placeholder="Ej: 2.5"
                      value={waterAmount}
                      onChange={(e) => setWaterAmount(e.target.value)}
                      style={inputStyle}
                    />
                  </div>
                </div>

                <div style={formField}>
                  <label style={labelStyle}>Recomendaciones de riego</label>
                  <textarea
                    placeholder="Ej: Riego moderado, evitar encharcamiento..."
                    value={irrigationRecommendations}
                    onChange={(e) => setIrrigationRecommendations(e.target.value)}
                    style={{ ...inputStyle, minHeight: "80px", resize: "vertical" }}
                  />
                </div>
              </div>

              <div style={formSection}>
                <h3 style={sectionTitle}>🌡️ Requisitos ambientales (opcional)</h3>
                <div style={formGrid}>
                  <div style={formField}>
                    <label style={labelStyle}>Exposición solar</label>
                    <select
                      value={sunExposure}
                      onChange={(e) => setSunExposure(e.target.value)}
                      style={inputStyle}
                    >
                      <option value="full_sun">Sol pleno</option>
                      <option value="partial">Sombra parcial</option>
                      <option value="shade">Sombra</option>
                    </select>
                  </div>

                  <div style={formField}>
                    <label style={labelStyle}>Temperatura mínima (°C)</label>
                    <input
                      type="number"
                      placeholder="Ej: 15"
                      value={minTemp}
                      onChange={(e) => setMinTemp(e.target.value)}
                      style={inputStyle}
                    />
                  </div>

                  <div style={formField}>
                    <label style={labelStyle}>Temperatura máxima (°C)</label>
                    <input
                      type="number"
                      placeholder="Ej: 30"
                      value={maxTemp}
                      onChange={(e) => setMaxTemp(e.target.value)}
                      style={inputStyle}
                    />
                  </div>

                  <div style={formField}>
                    <label style={{ ...labelStyle, display: "flex", alignItems: "center", gap: "8px" }}>
                      <input
                        type="checkbox"
                        checked={frostTolerance}
                        onChange={(e) => setFrostTolerance(e.target.checked)}
                        style={{ width: "16px", height: "16px" }}
                      />
                      Tolerante a heladas
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div style={modalFooter}>
              <button 
                style={secondaryButton} 
                onClick={() => {
                  setShowCreateModal(false);
                  resetForm();
                  setError(null);
                  setMessage(null);
                }}
              >
                Cancelar
              </button>
              <button style={primaryButton} onClick={handleCreateCrop} disabled={saving}>
                {saving ? "Guardando..." : "🌱 Crear cultivo"}
              </button>
            </div>
          </div>
        </div>
      )}

      <section style={gridSection}>
        {crops.length === 0 ? (
          <p style={emptyText}>No hay cultivos aún. Añade uno en el formulario.</p>
        ) : (
          <>
            <div style={catalogMeta}>
              <span>
                {pagination.total} cultivo{pagination.total === 1 ? "" : "s"}
              </span>
              <span>
                Pagina {pagination.page} de {pagination.total_pages}
              </span>
            </div>

            <div style={gridStyle}>
              {crops.map((crop) => (
                <article
                  key={crop.id}
                  style={{ ...cardStyle, cursor: "pointer" }}
                  onClick={() => {
                    setSelectedCrop(crop);
                    setShowModal(true);
                  }}
                >
                  <img
                    src={resolveCropImageSrc(crop.image_url)}
                    alt={crop.name}
                    style={cardImage}
                    onError={handleImageError}
                  />

                  <div style={cardBody}>
                    <div style={cardHeader}>
                      <div>
                        <h3 style={cropName}>{crop.name}</h3>
                        <p style={cropType}>{crop.type}</p>
                      </div>
                      <button
                        type="button"
                        onClick={(event) => {
                          event.preventDefault();
                          event.stopPropagation();
                          setSelectedCrop(crop);
                          setShowModal(true);
                        }}
                        style={toggleButton}
                        aria-label="Ver detalles"
                      >
                        🔎
                      </button>
                    </div>

                    <div style={badgeRow}>
                      <span style={badge}>Ciclo: {crop.life_cycle}</span>
                      {crop.irrigation && (
                        <span style={badge}>💧 {translateWateringFrequency(crop.irrigation.watering_frequency)}</span>
                      )}
                      {crop.environmental && (
                        <span style={badge}>🌡️ {crop.environmental.min_temp}°-{crop.environmental.max_temp}°</span>
                      )}
                    </div>
                  </div>
                </article>
              ))}
            </div>

            <div style={paginationBar}>
              <button
                type="button"
                style={paginationButton}
                onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                disabled={pagination.page <= 1}
              >
                Anterior
              </button>
              <span style={pageIndicator}>
                {pagination.page} / {pagination.total_pages}
              </span>
              <button
                type="button"
                style={paginationButton}
                onClick={() => setCurrentPage((prev) => Math.min(prev + 1, pagination.total_pages))}
                disabled={pagination.page >= pagination.total_pages}
              >
                Siguiente
              </button>
            </div>

            {showModal && selectedCrop && (
              <div style={modalOverlay}>
                <button
                  onClick={goToPrevCrop}
                  style={{
                    ...sideNavButton,
                    visibility: prevCrop ? "visible" : "hidden",
                  }}
                  aria-label="Cultivo anterior"
                >
                  <img src={leftArrowIcon} alt="Anterior" style={sideNavIcon} />
                </button>
                <div className="crop-modal-content" style={modalContent}>
                  <article style={detailCardStyle}>
                    <div style={detailHeader}>
                      <div>
                        <h2 style={detailTitle}>{selectedCrop.name}</h2>
                        <p style={detailSubtitle}>{selectedCrop.type}</p>
                      </div>
                      <button
                        onClick={() => {
                          setShowModal(false);
                          setSelectedCrop(null);
                          setEditMode(false);
                          resetForm();
                        }}
                        style={closeButton}
                      >
                        ✕
                      </button>
                    </div>

                    <img
                      src={resolveCropImageSrc(selectedCrop.image_url)}
                      alt={selectedCrop.name}
                      style={detailImage}
                      onError={handleImageError}
                    />

                    {error && <p style={statusError}>{error}</p>}
                    {message && <p style={statusSuccess}>{message}</p>}

                    {editMode ? (
                      <div style={editPanel}>
                        <div style={formSection}>
                          <h3 style={sectionTitle}>Información básica</h3>
                          <div style={formGrid}>
                            <div style={formField}>
                              <label style={labelStyle}>Nombre</label>
                              <input value={name} onChange={(e) => setName(e.target.value)} style={inputStyle} />
                            </div>
                            <div style={formField}>
                              <label style={labelStyle}>Tipo</label>
                              <input value={type} onChange={(e) => setType(e.target.value)} style={inputStyle} />
                            </div>
                            <div style={formField}>
                              <label style={labelStyle}>Ciclo de vida</label>
                              <select value={lifeCycle} onChange={(e) => setLifeCycle(e.target.value)} style={inputStyle}>
                                <option value="anual">Anual</option>
                                <option value="bienal">Bienal</option>
                                <option value="perenne">Perenne</option>
                              </select>
                            </div>
                          </div>
                        </div>

                        <div style={formSection}>
                          <h3 style={sectionTitle}>Riego</h3>
                          <div style={formGrid}>
                            <div style={formField}>
                              <label style={labelStyle}>Frecuencia</label>
                              <select value={wateringFrequency} onChange={(e) => setWateringFrequency(e.target.value)} style={inputStyle}>
                                <option value="daily">Diario</option>
                                <option value="2 times/week">2 veces por semana</option>
                                <option value="3 times/week">3 veces por semana</option>
                                <option value="weekly">Semanal</option>
                              </select>
                            </div>
                            <div style={formField}>
                              <label style={labelStyle}>Agua</label>
                              <input type="number" step="0.1" value={waterAmount} onChange={(e) => setWaterAmount(e.target.value)} style={inputStyle} />
                            </div>
                          </div>
                          <div style={formField}>
                            <label style={labelStyle}>Recomendaciones</label>
                            <textarea value={irrigationRecommendations} onChange={(e) => setIrrigationRecommendations(e.target.value)} style={{ ...inputStyle, minHeight: "76px", resize: "vertical" }} />
                          </div>
                        </div>

                        <div style={formSection}>
                          <h3 style={sectionTitle}>Ambiente</h3>
                          <div style={formGrid}>
                            <div style={formField}>
                              <label style={labelStyle}>Exposición solar</label>
                              <select value={sunExposure} onChange={(e) => setSunExposure(e.target.value)} style={inputStyle}>
                                <option value="full_sun">Sol pleno</option>
                                <option value="partial">Sombra parcial</option>
                                <option value="shade">Sombra</option>
                              </select>
                            </div>
                            <div style={formField}>
                              <label style={labelStyle}>Temperatura mínima</label>
                              <input type="number" value={minTemp} onChange={(e) => setMinTemp(e.target.value)} style={inputStyle} />
                            </div>
                            <div style={formField}>
                              <label style={labelStyle}>Temperatura máxima</label>
                              <input type="number" value={maxTemp} onChange={(e) => setMaxTemp(e.target.value)} style={inputStyle} />
                            </div>
                            <div style={formField}>
                              <label style={{ ...labelStyle, display: "flex", alignItems: "center", gap: "8px" }}>
                                <input type="checkbox" checked={frostTolerance} onChange={(e) => setFrostTolerance(e.target.checked)} />
                                Tolerante a heladas
                              </label>
                            </div>
                          </div>
                        </div>

                        <div style={formSection}>
                          <h3 style={sectionTitle}>Fases y quincenas</h3>
                          <div style={formGrid}>
                            <PhaseSelectors label="Siembra" value={plantingStart} onChange={setPlantingStart} />
                            <PhaseSelectors label="Trasplante" value={transplantStart} onChange={setTransplantStart} />
                            <PhaseSelectors label="Cosecha" value={harvestStart} onChange={setHarvestStart} />
                          </div>
                          <p style={infoTextMuted}>Solo importan el mes y la quincena. El año se ignora.</p>
                        </div>

                        <div style={editActions}>
                          <button style={secondaryButton} onClick={() => setEditMode(false)} disabled={saving}>
                            Cancelar
                          </button>
                          <button style={primaryButton} onClick={handleSaveCropDetails} disabled={saving}>
                            {saving ? "Guardando..." : "Guardar cambios"}
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div style={editActions}>
                        <button style={secondaryButton} onClick={beginEditCrop}>
                          Editar cultivo
                        </button>
                        <button style={primaryButton} onClick={handleActivateCalendar} disabled={saving}>
                          {selectedCrop.calendar?.is_active ? "Actualizar calendario" : "Añadir al calendario"}
                        </button>
                        <button style={dangerButton} onClick={handleDeleteCrop} disabled={saving}>
                          {saving ? "Quitando..." : "Quitar de mis cultivos"}
                        </button>
                      </div>
                    )}

                    <div style={infoBlock}>
                      <h4 style={infoTitle}>Detalles generales</h4>
                      <p style={infoText}>Ciclo: {selectedCrop.life_cycle}</p>
                      <p style={infoText}>Usuario: {selectedCrop.user_id}</p>
                    </div>

                    <div style={infoBlock}>
                      <h4 style={infoTitle}>Riego</h4>
                      {selectedCrop.irrigation ? (
                        <>
                          <p style={infoText}>
                            Frecuencia: {translateWateringFrequency(selectedCrop.irrigation.watering_frequency)}
                          </p>
                          <p style={infoText}>Agua: {selectedCrop.irrigation.water_amount}</p>
                          {selectedCrop.irrigation.recommendations && (
                            <p style={infoText}>
                              Recomendaciones: {selectedCrop.irrigation.recommendations}
                            </p>
                          )}
                        </>
                      ) : (
                        <p style={infoTextMuted}>Sin datos de riego</p>
                      )}
                    </div>

                    <div style={infoBlock}>
                      <h4 style={infoTitle}>Ambiente</h4>
                      {selectedCrop.environmental ? (
                        <>
                          <p style={infoText}>
                            Temperatura: {selectedCrop.environmental.min_temp}° / {selectedCrop.environmental.max_temp}°
                          </p>
                          <p style={infoText}>
                            Exposición: {translateSunExposure(selectedCrop.environmental.sun_exposure)}
                          </p>
                        </>
                      ) : (
                        <p style={infoTextMuted}>Sin datos ambientales</p>
                      )}
                    </div>

                    <div style={infoBlock}>
                      <h4 style={infoTitle}>Calendario</h4>
                      {selectedCrop.calendar ? (
                        <>
                          <p style={infoText}>Siembra: {selectedCrop.calendar.planting_start || "Sin inicio"} / {selectedCrop.calendar.planting_end || "Sin fin"}</p>
                          <p style={infoText}>Trasplante: {selectedCrop.calendar.transplant_start || "Sin inicio"} / {selectedCrop.calendar.transplant_end || "Sin fin"}</p>
                          <p style={infoText}>Cosecha: {selectedCrop.calendar.harvest_start || "Sin inicio"} / {selectedCrop.calendar.harvest_end || "Sin fin"}</p>
                          <p style={infoText}>Estado: {selectedCrop.calendar.is_active ? "Activo en calendario" : "Pendiente de activar"}</p>
                        </>
                      ) : (
                        <p style={infoTextMuted}>Sin fases configuradas</p>
                      )}
                    </div>

                    <button
                      onClick={() => {
                        setShowModal(false);
                        setSelectedCrop(null);
                        navigate(`/tasks?cropId=${selectedCrop.id}`);
                      }}
                      style={{
                        ...viewTasksButtonStyle,
                        backgroundColor: "#10B981",
                        width: "auto",
                        alignSelf: "flex-start",
                      }}
                    >
                      ➕ Crear Tarea
                    </button>

                    <CropTasks cropId={selectedCrop.id} userId={currentUser?.user_id} token={token} />
                  </article>
                </div>
                <button
                  onClick={goToNextCrop}
                  style={{
                    ...sideNavButton,
                    visibility: nextCrop ? "visible" : "hidden",
                  }}
                  aria-label="Próximo cultivo"
                >
                  <img src={rightArrowIcon} alt="Siguiente" style={sideNavIcon} />
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </div>
    </>
  );
}

const page = {
  minHeight: "100vh",
  padding: "32px",
  background: "#F4FBF6",
  fontFamily: "Inter, Arial, sans-serif",
};

const headerStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "16px",
  marginBottom: "28px",
};

const titleStyle = {
  margin: 0,
  fontSize: "2.5rem",
  color: "#1E4E2E",
};

const subtitleStyle = {
  marginTop: "10px",
  color: "#4D6A5E",
  fontSize: "1rem",
  maxWidth: "520px",
};

const sectionTitle = {
  margin: 0,
  marginBottom: "18px",
  color: "#264F37",
  fontSize: "1.3rem",
};

const formGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
  gap: "16px",
  marginBottom: "18px",
};

const inputStyle = {
  width: "100%",
  padding: "14px 16px",
  borderRadius: "16px",
  border: "1px solid #D7E7D8",
  background: "#F8FBF8",
  color: "#1F3D2E",
  fontSize: "0.98rem",
};

const primaryButton = {
  padding: "14px 24px",
  borderRadius: "16px",
  border: "none",
  background: "linear-gradient(135deg, #2F8F4C 0%, #5CAF75 100%)",
  color: "white",
  fontWeight: 700,
  cursor: "pointer",
  boxShadow: "0 14px 28px rgba(47, 143, 76, 0.24)",
  transition: "transform 180ms ease, box-shadow 180ms ease",
};

const secondaryButton = {
  padding: "12px 20px",
  borderRadius: "16px",
  border: "1px solid #C8D8CB",
  background: "white",
  color: "#2E7D32",
  cursor: "pointer",
  boxShadow: "0 8px 18px rgba(46, 125, 50, 0.08)",
};

const dangerButton = {
  padding: "12px 20px",
  borderRadius: "16px",
  border: "1px solid #F3B8B8",
  background: "#FFF7F7",
  color: "#B42318",
  cursor: "pointer",
  boxShadow: "0 8px 18px rgba(180, 35, 24, 0.08)",
  fontWeight: 700,
};

const statusSuccess = {
  marginTop: "18px",
  color: "#2E7D32",
  fontWeight: 600,
};

const statusError = {
  marginTop: "18px",
  color: "#9B2C2C",
  fontWeight: 600,
};

const previewWrapper = {
  marginBottom: "18px",
  padding: "18px",
  borderRadius: "20px",
  background: "#F7FCF6",
  border: "1px solid rgba(126, 186, 137, 0.16)",
};

const previewLabel = {
  margin: "0 0 12px 0",
  color: "#2E593F",
  fontWeight: 700,
};

const previewImage = {
  width: "100%",
  maxWidth: "280px",
  aspectRatio: "4 / 3",
  objectFit: "cover",
  borderRadius: "18px",
  boxShadow: "0 14px 30px rgba(15, 23, 42, 0.12)",
};

const gridSection = {
  maxWidth: "1180px",
  margin: "0 auto",
};

const catalogMeta = {
  marginBottom: "16px",
  color: "#4D6A5E",
  fontWeight: 700,
  display: "flex",
  justifyContent: "space-between",
  gap: "12px",
  flexWrap: "wrap",
};

const gridStyle = {
  display: "grid",
  gap: "24px",
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
};

const paginationBar = {
  marginTop: "26px",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  gap: "12px",
};

const paginationButton = {
  padding: "12px 18px",
  borderRadius: "14px",
  border: "1px solid #C8D8CB",
  background: "white",
  color: "#2E7D32",
  cursor: "pointer",
  fontWeight: 700,
};

const pageIndicator = {
  color: "#2E593F",
  fontWeight: 800,
};

const cardStyle = {
  borderRadius: "28px",
  overflow: "hidden",
  background: "white",
  boxShadow: "0 24px 60px rgba(15, 23, 42, 0.12)",
  display: "flex",
  flexDirection: "column",
  transition: "transform 180ms ease, box-shadow 180ms ease",
};

const cardImage = {
  width: "100%",
  aspectRatio: "4 / 3",
  objectFit: "cover",
  backgroundColor: "#E8F3EA",
};

const cardBody = {
  padding: "22px",
  display: "flex",
  flexDirection: "column",
  gap: "14px",
};

const cropName = {
  margin: 0,
  fontSize: "1.35rem",
  color: "#15452A",
};

const cropType = {
  margin: 0,
  color: "#5A6E60",
};

const badgeRow = {
  display: "flex",
  flexWrap: "wrap",
  gap: "10px",
  alignItems: "center",
};

const badge = {
  display: "inline-flex",
  padding: "8px 12px",
  borderRadius: "999px",
  background: "#E8F6EA",
  color: "#2E7D32",
  fontWeight: 700,
  fontSize: "0.9rem",
};

const cardHeader = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "12px",
};

const toggleButton = {
  background: "transparent",
  border: "1px solid #C8D8CB",
  borderRadius: "999px",
  color: "#2E593F",
  padding: "8px 12px",
  cursor: "pointer",
  fontWeight: 700,
  minWidth: "52px",
};

const sideNavButton = {
  background: "#F7FBF7",
  border: "1px solid rgba(126, 186, 137, 0.3)",
  borderRadius: "50%",
  padding: "12px",
  cursor: "pointer",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  boxShadow: "0 12px 24px rgba(15, 23, 42, 0.08)",
  minWidth: "52px",
  minHeight: "52px",
};

const sideNavIcon = {
  width: "24px",
  height: "24px",
};

const detailCardStyle = {
  borderRadius: "28px",
  padding: "28px",
  background: "white",
  boxShadow: "0 24px 60px rgba(15, 23, 42, 0.12)",
  display: "flex",
  flexDirection: "column",
  gap: "18px",
  maxHeight: "80vh",
  overflowY: "auto",
};

const detailHeader = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "12px",
};

const detailTitle = {
  margin: 0,
  fontSize: "1.8rem",
  color: "#1E4E2E",
};

const detailSubtitle = {
  margin: "8px 0 0",
  color: "#5A6E60",
};

const detailImage = {
  width: "100%",
  aspectRatio: "4 / 3",
  objectFit: "cover",
  borderRadius: "20px",
  backgroundColor: "#E8F3EA",
};

const infoBlock = {
  padding: "18px",
  borderRadius: "20px",
  background: "#F7FCF6",
  border: "1px solid rgba(126, 186, 137, 0.16)",
  display: "flex",
  flexDirection: "column",
  gap: "6px",
};

const editPanel = {
  padding: "18px",
  borderRadius: "20px",
  background: "#FBFEFB",
  border: "1px solid rgba(126, 186, 137, 0.22)",
  display: "flex",
  flexDirection: "column",
  gap: "24px",
};

const editActions = {
  display: "flex",
  flexWrap: "wrap",
  gap: "12px",
  alignItems: "center",
};

const infoTitle = {
  margin: 0,
  color: "#2E593F",
  fontWeight: 700,
};

const viewTasksButtonStyle = {
  width: "100%",
  padding: "12px 16px",
  marginTop: "12px",
  borderRadius: "8px",
  border: "none",
  color: "white",
  fontWeight: "600",
  cursor: "pointer",
  fontSize: "0.95rem",
  transition: "background-color 0.2s ease",
};

const infoText = {
  margin: 0,
  color: "#4C6959",
  lineHeight: 1.6,
};

const infoTextMuted = {
  margin: 0,
  color: "#7A8A80",
  fontStyle: "italic",
};

const emptyText = {
  margin: 0,
  padding: "24px",
  borderRadius: "20px",
  background: "#F0F7EE",
  color: "#5E7160",
  textAlign: "center",
};

const modalOverlay = {
  position: "fixed",
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: "rgba(0, 0, 0, 0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  gap: "16px",
  padding: "20px",
  zIndex: 1000,
};

const modalContent = {
  maxWidth: "900px",
  width: "90%",
  maxHeight: "90vh",
  overflowY: "auto",
  padding: "20px",
};

const closeButton = {
  background: "transparent",
  border: "1px solid #C8D8CB",
  borderRadius: "50%",
  color: "#2E593F",
  padding: "8px 12px",
  cursor: "pointer",
  fontWeight: 700,
  fontSize: "1.2rem",
  width: "40px",
  height: "40px",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};

const createModalContent = {
  maxWidth: "800px",
  width: "90%",
  maxHeight: "90vh",
  background: "white",
  borderRadius: "28px",
  boxShadow: "0 24px 60px rgba(15, 23, 42, 0.15)",
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
};

const modalHeader = {
  padding: "28px 28px 0 28px",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  borderBottom: "1px solid #E8F3EA",
  paddingBottom: "20px",
};

const modalTitle = {
  margin: 0,
  fontSize: "1.8rem",
  color: "#1E4E2E",
};

const modalBody = {
  padding: "28px",
  display: "flex",
  flexDirection: "column",
  gap: "32px",
  flex: 1,
  overflowY: "auto",
  maxHeight: "calc(90vh - 140px)",
};

const modalFooter = {
  padding: "0 28px 28px 28px",
  display: "flex",
  justifyContent: "flex-end",
  gap: "12px",
  borderTop: "1px solid #E8F3EA",
  paddingTop: "20px",
};

const formSection = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
};

const formField = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
};

const labelStyle = {
  fontWeight: 600,
  color: "#2E593F",
  fontSize: "0.95rem",
};
