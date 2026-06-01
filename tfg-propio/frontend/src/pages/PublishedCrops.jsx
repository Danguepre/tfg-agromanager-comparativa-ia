import { useCallback, useEffect, useState } from "react";
import { addPublishedCropToMyCrops, getPublishedCrops } from "../api/api";
import { defaultCropImage, resolveCropImageSrc } from "../utils/cropImages";
import { translateSunExposure, translateWateringFrequency } from "../utils/translations";

const getCatalogSourceId = (crop) => crop.source_crop_id || crop.id;
const PAGE_SIZE = 12;

export default function PublishedCrops({ token }) {
  const [crops, setCrops] = useState([]);
  const [types, setTypes] = useState([]);
  const [nameFilter, setNameFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: PAGE_SIZE,
    total_pages: 1,
  });
  const [loading, setLoading] = useState(true);
  const [addingCropId, setAddingCropId] = useState(null);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const loadPublishedCrops = useCallback(async () => {
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const data = await getPublishedCrops(token, {
        name: nameFilter,
        type: typeFilter,
        page,
        page_size: PAGE_SIZE,
      });
      setCrops(data.items || []);
      setTypes(data.types || []);
      setPagination({
        total: data.total || 0,
        page: data.page || 1,
        page_size: data.page_size || PAGE_SIZE,
        total_pages: data.total_pages || 1,
      });
    } catch (err) {
      setError(err.message || "No se pudieron cargar los cultivos del catalogo");
    } finally {
      setLoading(false);
    }
  }, [nameFilter, page, token, typeFilter]);

  useEffect(() => {
    loadPublishedCrops();
  }, [loadPublishedCrops]);

  const handleNameFilterChange = (event) => {
    setNameFilter(event.target.value);
    setPage(1);
  };

  const handleTypeFilterChange = (event) => {
    setTypeFilter(event.target.value);
    setPage(1);
  };

  const clearFilters = () => {
    setNameFilter("");
    setTypeFilter("");
    setPage(1);
  };

  const hasFilters = nameFilter.trim() || typeFilter;

  const handleAddCrop = async (crop) => {
    setAddingCropId(crop.id);
    setError(null);
    setMessage(null);

    try {
      await addPublishedCropToMyCrops(token, crop.id);
      const sourceId = getCatalogSourceId(crop);
      setCrops((prev) =>
        prev.map((item) =>
          getCatalogSourceId(item) === sourceId
            ? { ...item, added_to_my_crops: true }
            : item
        )
      );
      setMessage(`${crop.name} se ha anadido a tus cultivos`);
    } catch (err) {
      setError(err.message || "No se pudo anadir el cultivo");
    } finally {
      setAddingCropId(null);
    }
  };

  const handleImageError = (event) => {
    event.currentTarget.onerror = null;
    event.currentTarget.src = defaultCropImage;
  };

  return (
    <div style={pageStyle}>
      <header style={headerStyle}>
        <div>
          <h1 style={titleStyle}>Catalogo de cultivos</h1>
          <p style={subtitleStyle}>
            Anade cualquier cultivo existente a tu espacio personal como una copia independiente.
          </p>
        </div>
        <div style={headerActions}>
          <button style={secondaryButton} onClick={loadPublishedCrops}>
            Actualizar
          </button>
        </div>
      </header>

      {message && <p style={statusSuccess}>{message}</p>}
      {error && <p style={statusError}>{error}</p>}

      <section style={filtersPanel}>
        <div style={filterField}>
          <label style={labelStyle}>Nombre</label>
          <input
            type="search"
            placeholder="Buscar por nombre"
            value={nameFilter}
            onChange={handleNameFilterChange}
            style={inputStyle}
          />
        </div>

        <div style={filterField}>
          <label style={labelStyle}>Tipo</label>
          <select value={typeFilter} onChange={handleTypeFilterChange} style={inputStyle}>
            <option value="">Todos los tipos</option>
            {types.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          style={{
            ...secondaryButton,
            opacity: hasFilters ? 1 : 0.65,
            cursor: hasFilters ? "pointer" : "not-allowed",
          }}
          onClick={clearFilters}
          disabled={!hasFilters}
        >
          Limpiar filtros
        </button>
      </section>

      <section style={gridSection}>
        {loading ? (
          <p style={emptyText}>Cargando cultivos del catalogo...</p>
        ) : crops.length === 0 ? (
          <p style={emptyText}>No hay cultivos que coincidan con los filtros.</p>
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
                <article key={crop.id} style={cardStyle}>
                  <img
                    src={resolveCropImageSrc(crop.image_url)}
                    alt={crop.name}
                    style={cardImage}
                    onError={handleImageError}
                  />

                  <div style={cardBody}>
                    <div>
                      <h3 style={cropName}>{crop.name}</h3>
                      <p style={cropType}>{crop.type}</p>
                    </div>

                    <div style={badgeRow}>
                      <span style={badge}>Ciclo: {crop.life_cycle}</span>
                      {crop.irrigation && (
                        <span style={badge}>
                          Riego: {translateWateringFrequency(crop.irrigation.watering_frequency)}
                        </span>
                      )}
                      {crop.environmental && (
                        <span style={badge}>
                          Ambiente: {translateSunExposure(crop.environmental.sun_exposure)}
                        </span>
                      )}
                      {crop.added_to_my_crops && (
                        <span style={addedBadge}>Anadido</span>
                      )}
                    </div>

                    <button
                      type="button"
                      style={{
                        ...(crop.added_to_my_crops ? addedButton : primaryButton),
                        opacity: addingCropId === crop.id ? 0.75 : 1,
                        cursor: addingCropId === crop.id ? "wait" : crop.added_to_my_crops ? "not-allowed" : "pointer",
                      }}
                      onClick={() => handleAddCrop(crop)}
                      disabled={addingCropId === crop.id || crop.added_to_my_crops}
                    >
                      {crop.added_to_my_crops
                        ? "Anadido"
                        : addingCropId === crop.id
                          ? "Anadiendo..."
                          : "Anadir a mis cultivos"}
                    </button>
                  </div>
                </article>
              ))}
            </div>

            <div style={paginationBar}>
              <button
                type="button"
                style={paginationButton}
                onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
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
                onClick={() => setPage((prev) => Math.min(prev + 1, pagination.total_pages))}
                disabled={pagination.page >= pagination.total_pages}
              >
                Siguiente
              </button>
            </div>
          </>
        )}
      </section>
    </div>
  );
}

const pageStyle = {
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

const headerActions = {
  display: "flex",
  gap: "12px",
  alignItems: "center",
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
  maxWidth: "560px",
};

const gridSection = {
  maxWidth: "1180px",
  margin: "0 auto",
};

const filtersPanel = {
  maxWidth: "1180px",
  margin: "0 auto 24px",
  padding: "20px",
  borderRadius: "20px",
  background: "white",
  boxShadow: "0 14px 34px rgba(15, 23, 42, 0.08)",
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: "16px",
  alignItems: "end",
};

const filterField = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
};

const labelStyle = {
  fontWeight: 700,
  color: "#2E593F",
  fontSize: "0.95rem",
};

const inputStyle = {
  width: "100%",
  padding: "12px 14px",
  borderRadius: "14px",
  border: "1px solid #D7E7D8",
  background: "#F8FBF8",
  color: "#1F3D2E",
  fontSize: "0.98rem",
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
  gridTemplateColumns: "repeat(auto-fill, minmax(280px, 320px))",
  justifyContent: "start",
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
  gap: "16px",
  flex: 1,
};

const cropName = {
  margin: 0,
  fontSize: "1.35rem",
  color: "#15452A",
};

const cropType = {
  margin: "6px 0 0",
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

const addedBadge = {
  display: "inline-flex",
  padding: "8px 12px",
  borderRadius: "999px",
  background: "#DCFCE7",
  color: "#166534",
  fontWeight: 800,
  fontSize: "0.9rem",
};

const primaryButton = {
  marginTop: "auto",
  padding: "14px 18px",
  borderRadius: "16px",
  border: "none",
  background: "linear-gradient(135deg, #2F8F4C 0%, #5CAF75 100%)",
  color: "white",
  fontWeight: 700,
  cursor: "pointer",
  boxShadow: "0 14px 28px rgba(47, 143, 76, 0.24)",
};

const addedButton = {
  marginTop: "auto",
  padding: "14px 18px",
  borderRadius: "16px",
  border: "1px solid #BBF7D0",
  background: "#DCFCE7",
  color: "#166534",
  fontWeight: 800,
  cursor: "not-allowed",
  boxShadow: "none",
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

const emptyText = {
  margin: 0,
  padding: "24px",
  borderRadius: "20px",
  background: "#F0F7EE",
  color: "#5E7160",
  textAlign: "center",
};
