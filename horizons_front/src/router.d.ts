import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?:  boolean
    requiresGuest?: boolean
    public?:        boolean
    fullWidth?:     boolean
    fillHeight?:    boolean
  }
}