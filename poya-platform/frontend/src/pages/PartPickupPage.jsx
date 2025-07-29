import React, { useEffect, useState, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Box, 
  Button, 
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  LinearProgress
} from '@mui/material';
import { Upload as UploadIcon } from '@mui/icons-material';
import { fetchPickupTasks, uploadInvoice, confirmPickup } from '../store/partPickupSlice';

const PartPickupPage = () => {
  const dispatch = useDispatch();
  const { tasks, loading, error, uploadProgress } = useSelector((state) => state.partPickup);
  
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [notes, setNotes] = useState('');
  const [quantityReceived, setQuantityReceived] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [invoiceUrl, setInvoiceUrl] = useState('');
  const fileInputRef = useRef();

  useEffect(() => {
    dispatch(fetchPickupTasks());
  }, [dispatch]);

  const handleOpenDialog = (task) => {
    setSelectedTask(task);
    setOpenDialog(true);
    setNotes('');
    setQuantityReceived('');
    setSelectedFile(null);
    setInvoiceUrl('');
  };

  const handleCloseDialog = () => {
    setSelectedTask(null);
    setOpenDialog(false);
    setNotes('');
    setQuantityReceived('');
    setSelectedFile(null);
    setInvoiceUrl('');
  };

  const handleFileSelect = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (selectedFile) {
      const result = await dispatch(uploadInvoice(selectedFile));
      if (!result.error) {
        setInvoiceUrl(result.payload.invoice_url);
      }
    }
  };

  const handleConfirmPickup = async () => {
    if (!quantityReceived || !invoiceUrl) {
      return;
    }

    await dispatch(confirmPickup({
      taskId: selectedTask.id,
      quantityReceived: parseInt(quantityReceived, 10),
      invoiceUrl,
      notes
    }));

    handleCloseDialog();
  };

  if (loading && tasks.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Part Pickup Tasks
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error.message || 'An error occurred'}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Task ID</TableCell>
              <TableCell>Route Card</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tasks.map((task) => (
              <TableRow key={task.id}>
                <TableCell>{task.id}</TableCell>
                <TableCell>{task.route_card_id}</TableCell>
                <TableCell>{task.description}</TableCell>
                <TableCell>{new Date(task.due_date).toLocaleString()}</TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleOpenDialog(task)}
                  >
                    Confirm Pickup
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Confirm Part Pickup</DialogTitle>
        <DialogContent>
          <Box mt={2} display="flex" flexDirection="column" gap={2}>
            <TextField
              label="Quantity Received"
              type="number"
              value={quantityReceived}
              onChange={(e) => setQuantityReceived(e.target.value)}
              fullWidth
            />

            <Box>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                style={{ display: 'none' }}
                ref={fileInputRef}
                onChange={handleFileSelect}
              />
              <Box display="flex" alignItems="center" gap={2}>
                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                  onClick={() => fileInputRef.current.click()}
                >
                  Select Invoice
                </Button>
                {selectedFile && (
                  <Button
                    variant="contained"
                    onClick={handleUpload}
                    disabled={loading}
                  >
                    Upload
                  </Button>
                )}
              </Box>
              {selectedFile && (
                <Typography variant="body2" mt={1}>
                  Selected file: {selectedFile.name}
                </Typography>
              )}
              {uploadProgress > 0 && uploadProgress < 100 && (
                <Box mt={1}>
                  <LinearProgress variant="determinate" value={uploadProgress} />
                </Box>
              )}
              {invoiceUrl && (
                <Alert severity="success" sx={{ mt: 1 }}>
                  Invoice uploaded successfully
                </Alert>
              )}
            </Box>

            <TextField
              label="Notes"
              multiline
              rows={4}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleConfirmPickup}
            color="primary"
            variant="contained"
            disabled={!quantityReceived || !invoiceUrl || loading}
          >
            Confirm Pickup
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PartPickupPage;
