import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { UploadPortal } from './pages/UploadPortal';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/upload/:referenceId" element={<UploadPortal />} />
        {/* Redirect root to a dummy reference for demo purposes */}
        <Route path="/" element={<Navigate to="/upload/demo-guid-1234" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
