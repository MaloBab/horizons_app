import { ref } from 'vue'

export interface WeatherInfo {
  temperature: number
  weatherCode: number
  windspeed: number
  description: string
  icon: string
}

// Codes WMO → description + emoji nautique
function interpretWeather(code: number): { description: string; icon: string } {
  if (code === 0)                    return { description: 'Ciel dégagé',    icon: '☀️' }
  if (code <= 2)                     return { description: 'Peu nuageux',    icon: '🌤️' }
  if (code <= 3)                     return { description: 'Couvert',        icon: '☁️' }
  if (code <= 49)                    return { description: 'Brumeux',        icon: '🌫️' }
  if (code <= 59)                    return { description: 'Bruine',         icon: '🌦️' }
  if (code <= 69)                    return { description: 'Pluie',          icon: '🌧️' }
  if (code <= 79)                    return { description: 'Neige',          icon: '❄️' }
  if (code <= 84)                    return { description: 'Averses',        icon: '🌦️' }
  if (code <= 99)                    return { description: 'Orage',          icon: '⛈️' }
  return { description: 'Inconnu', icon: '🌊' }
}

export function useWeather() {
  const weather = ref<WeatherInfo | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchWeatherForDate(dateStr: string): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const url = new URL('https://api.open-meteo.com/v1/forecast')
      url.searchParams.set('latitude', '48.5870031')
      url.searchParams.set('longitude', '-4.5720236')
      url.searchParams.set('daily', 'temperature_2m_max,weathercode,windspeed_10m_max')
      url.searchParams.set('timezone', 'Europe/Paris')
      url.searchParams.set('start_date', dateStr)
      url.searchParams.set('end_date', dateStr)

      const res = await fetch(url.toString())
      if (!res.ok) throw new Error('Erreur météo')
      const data = await res.json()

      const code = data.daily.weathercode[0]
      const { description, icon } = interpretWeather(code)

      weather.value = {
        temperature: Math.round(data.daily.temperature_2m_max[0]),
        weatherCode: code,
        windspeed: Math.round(data.daily.windspeed_10m_max[0]),
        description,
        icon,
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erreur inconnue'
    } finally {
      isLoading.value = false
    }
  }

  return { weather, isLoading, error, fetchWeatherForDate }
}