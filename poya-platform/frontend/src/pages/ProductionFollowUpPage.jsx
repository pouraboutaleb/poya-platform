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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers';
import { fetchFollowUpTasks, logFollowUp } from '../store/productionFollowUpSlice';

const FOLLOW_UP_STATUSES = {
  ON_SCHEDULE: 'on_schedule',
  DELAYED: 'delayed',
  READY_FOR_PICKUP: 'ready_for_pickup'
};

const ProductionFollowUpPage = () => {
  const dispatch = useDispatch();
  const { tasks, loading, error } = useSelector((state) => state.productionFollowUp);
  
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [status, setStatus] = useState('');
  const [notes, setNotes] = useState('');
  const [revisedCompletionDate, setRevisedCompletionDate] = useState(null);

  useEffect(() => {
    dispatch(fetchFollowUpTasks());
  }, [dispatch]);

  const handleOpenDialog = (task) => {
    setSelectedTask(task);
    setStatus('');
    setNotes('');
    setRevisedCompletionDate(null);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setSelectedTask(null);
    setStatus('');
    setNotes('');
    setRevisedCompletionDate(null);
    setOpenDialog(false);
  };

  const handleSubmit = async () => {
    if (!status) return;

    // Validate that revised completion date is provided when status is DELAYED
    if (status === FOLLOW_UP_STATUSES.DELAYED && !revisedCompletionDate) {
      return;
    }

    await dispatch(logFollowUp({
      taskId: selectedTask.id,
      status,
      notes,
      revisedCompletionDate: status === FOLLOW_UP_STATUSES.DELAYED ? revisedCompletionDate : null
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
        Production Follow-up Tasks
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
                    Log Follow-up
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Log Follow-up</DialogTitle>
        <DialogContent>
          <Box mt={2} display="flex" flexDirection="column" gap={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={status}
                label="Status"
                onChange={(e) => setStatus(e.target.value)}
              >
                <MenuItem value={FOLLOW_UP_STATUSES.ON_SCHEDULE}>
                  On Schedule
                </MenuItem>
                <MenuItem value={FOLLOW_UP_STATUSES.DELAYED}>
                  Delayed
                </MenuItem>
                <MenuItem value={FOLLOW_UP_STATUSES.READY_FOR_PICKUP}>
                  Ready for Pickup
                </MenuItem>
              </Select>
            </FormControl>

            {status === FOLLOW_UP_STATUSES.DELAYED && (
              <DateTimePicker
                label="Revised Completion Date"
                value={revisedCompletionDate}
                onChange={setRevisedCompletionDate}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            )}

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
            onClick={handleSubmit}
            color="primary"
            variant="contained"
            disabled={!status || (status === FOLLOW_UP_STATUSES.DELAYED && !revisedCompletionDate)}
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProductionFollowUpPage;
