import type { UserShortResponse } from './user.types'

export interface Activity {
  id: number
  icon: string | null
  title: string
  action_type: string
  created_at: string
  user_id: string        
  author: UserShortResponse
}