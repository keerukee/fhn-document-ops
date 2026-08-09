import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { UploadPortal } from '../UploadPortal';
import { describe, it, expect, vi } from 'vitest';

// Mock the components that rely on icons or other complex logic if needed
vi.mock('../../components/layout/Header', () => ({ Header: () => <div data-testid="mock-header" /> }));
vi.mock('../../components/layout/Footer', () => ({ Footer: () => <div data-testid="mock-footer" /> }));
vi.mock('../../components/upload/FileDropzone', () => ({ 
  FileDropzone: ({ onFilesAccepted }: any) => (
    <button data-testid="mock-dropzone" onClick={() => onFilesAccepted([new File(["dummy content"], "test.pdf", { type: "application/pdf" })])}>
      Drop files here
    </button>
  )
}));

describe('UploadPortal Component', () => {
  const renderComponent = () => {
    return render(
      <MemoryRouter initialEntries={['/upload/TEST-1234']}>
        <Routes>
          <Route path="/upload/:referenceId" element={<UploadPortal />} />
        </Routes>
      </MemoryRouter>
    );
  };

  it('shows loading state initially and then renders request data', async () => {
    renderComponent();
    
    // Should show loading spinner initially (or at least wait for mock data to resolve)
    // The mock data setTimeout is 500ms
    await waitFor(() => {
      expect(screen.getByText(/Secure Document Upload/i)).toBeInTheDocument();
    }, { timeout: 1000 });

    expect(screen.getByText(/Required Documents/i)).toBeInTheDocument();
    expect(screen.getByText(/W-2 Form/i)).toBeInTheDocument();
  });

  it('allows uploading a file and then shows finish button when all docs are uploaded', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText(/Submit Documents/i)).toBeInTheDocument();
    }, { timeout: 1000 });

    // Upload a file using the mock dropzone
    fireEvent.click(screen.getByTestId('mock-dropzone'));
    fireEvent.click(screen.getByText(/Submit Documents/i));

    // Wait for the mock upload timeout (1500ms)
    await waitFor(() => {
      // Since there are 2 required documents in the mock data, and we uploaded 1 file,
      // it should show an alert (which is tricky to test in jsdom, but we can check UI state)
      // Actually we need to upload twice to get the Finish button.
      expect(screen.getByText(/Submit Documents/i)).toBeInTheDocument();
    }, { timeout: 2000 });
    
    // Upload the second file
    fireEvent.click(screen.getByTestId('mock-dropzone'));
    fireEvent.click(screen.getByText(/Submit Documents/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Finish & Lock Request/i)).toBeInTheDocument();
    }, { timeout: 2000 });
    
    // Click Finish
    fireEvent.click(screen.getByText(/Finish & Lock Request/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Upload Successful/i)).toBeInTheDocument();
    });
  });
});
