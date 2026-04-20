export type UserRole = 'admin' | 'user'

export interface UserResponse {
  id: string
  username: string
  email: string
  profile_picture_url: string | null
  role: UserRole
}

export interface UserShortResponse {
  username: string
  profile_picture_url: string | null
}

export interface UserUpdate {
  username?: string
  password?: string
  profile_picture_url?: string
}