import React, { useEffect, useState } from 'react';
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
  CircularProgress
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers';
import { fetchDeliveryTasks, confirmDelivery } from '../store/materialDeliverySlice';

const MaterialDeliveryPage = () => {
  const dispatch = useDispatch();
  const { tasks, loading, error } = useSelector((state) => state.materialDelivery);
  
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [notes, setNotes] = useState('');
  const [estimatedCompletionDate, setEstimatedCompletionDate] = useState(null);

  useEffect(() => {
    dispatch(fetchDeliveryTasks());
  }, [dispatch]);

  const handleOpenDialog = (task) => {
    setSelectedTask(task);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setSelectedTask(null);
    setNotes('');
    setEstimatedCompletionDate(null);
    setOpenDialog(false);
  };

  const handleConfirmDelivery = async () => {
    if (!estimatedCompletionDate) {
      return; // Add error handling/validation as needed
    }

    await dispatch(confirmDelivery({
      taskId: selectedTask.id,
      estimatedCompletionDate,
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
        Material Delivery Tasks
      </Typography>

      {error && (
        <Typography color="error" gutterBottom>
          {error.message || 'An error occurred'}
        </Typography>
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
                    Confirm Delivery
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Confirm Material Delivery</DialogTitle>
        <DialogContent>
          <Box mt={2}>
            <DateTimePicker
              label="Estimated Completion Date"
              value={estimatedCompletionDate}
              onChange={setEstimatedCompletionDate}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
            <TextField
              margin="normal"
              label="Notes"
              multiline
              rows={4}
              fullWidth
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleConfirmDelivery}
            color="primary"
            variant="contained"
            disabled={!estimatedCompletionDate}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MaterialDeliveryPage;
