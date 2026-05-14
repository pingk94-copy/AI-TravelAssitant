import { apiRequest } from './http'

export type TripPlanRequest = {
  origin: string
  destination: string
  start_date: string
  days: number
  budget?: string
  preferences: string[]
}

export type TripResponse = {
  id: number
  title: string
  origin: string
  destination: string
  start_date: string
  days: number
  budget: string | null
  preferences: string[]
  status: string
  result: {
    summary: string
    origin: string
    destination: string
    weather: Array<Record<string, string>>
    route_tips: string[]
    days: Array<{
      day: number
      theme: string
      schedule: Array<{
        time: string
        title: string
        description: string
      }>
    }>
    tips: string[]
  }
  created_at: string
}

export async function planTrip(token: string, payload: TripPlanRequest) {
  return apiRequest<TripResponse>('/api/trips/plan', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  })
}

export async function listTrips(token: string) {
  return apiRequest<TripResponse[]>('/api/trips', {
    headers: { Authorization: `Bearer ${token}` },
  })
}
