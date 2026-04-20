export interface FestivalResponse {
  id: string
  name: string
  edition: number
  start_date: string
  end_date: string
  location_name: string
  location_city: string
}

export type FestivalCreate = Omit<FestivalResponse, 'id'>

export type FestivalUpdate = Partial<FestivalCreate>