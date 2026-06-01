
export const translateWateringFrequency = (frequency) => {
  const translations = {
    "daily": "Diario",
    "2 times/week": "2 veces por semana",
    "3 times/week": "3 veces por semana",
    "weekly": "Semanal"
  };
  return translations[frequency] || frequency;
};

export const translateSunExposure = (exposure) => {
  const translations = {
    "full_sun": "Sol pleno",
    "partial": "Sombra parcial",
    "shade": "Sombra"
  };
  return translations[exposure] || exposure;
};

export const translateLifeCycle = (cycle) => {
  const translations = {
    "anual": "Anual",
    "bienal": "Bienal",
    "perenne": "Perenne"
  };
  return translations[cycle] || cycle;
};
