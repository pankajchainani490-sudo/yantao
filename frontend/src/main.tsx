import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Navigate, createBrowserRouter, RouterProvider } from 'react-router-dom'

import App from './App.tsx'
import './index.css'
import AppShell from './layouts/AppShell.tsx'
import SecurityScreenPage from './pages/SecurityScreenPage.tsx'
import { consoleRoutes } from './router/routes.tsx'

const consoleChildren = consoleRoutes.map(({ index, path, element }) =>
  index ? { index: true, element } : { path, element },
)

const router = createBrowserRouter([
  {
    element: <App />,
    children: [
      {
        path: '/',
        element: <SecurityScreenPage />,
      },
      {
        path: '/console',
        element: <AppShell />,
        children: consoleChildren,
      },
      { path: '/detection', element: <Navigate to="/console/detection" replace /> },
      { path: '/replay', element: <Navigate to="/console/replay" replace /> },
      { path: '/blacklist', element: <Navigate to="/console/blacklist" replace /> },
      { path: '/metrics', element: <Navigate to="/console/metrics" replace /> },
      { path: '/settings', element: <Navigate to="/console/settings" replace /> },
    ],
  },
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
