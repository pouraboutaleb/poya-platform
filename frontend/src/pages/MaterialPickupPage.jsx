import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  fetchPickupTasks,
  confirmPickup,
  setSelectedTask
} from '../../store/materialPickupSlice';

const MaterialPickupPage = () => {
  const dispatch = useDispatch();
  const { tasks, loading, error, selectedTask } = useSelector(
    state => state.materialPickup
  );
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchPickupTasks());
    // Refresh the list every 5 minutes
    const interval = setInterval(() => {
      dispatch(fetchPickupTasks());
    }, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [dispatch]);

  const handlePickupClick = (task) => {
    dispatch(setSelectedTask(task));
    setDialogOpen(true);
  };

  const handleConfirmPickup = async () => {
    if (selectedTask) {
      try {
        await dispatch(confirmPickup(selectedTask.id)).unwrap();
        setDialogOpen(false);
      } catch (error) {
        console.error('Error confirming pickup:', error);
      }
    }
  };

  if (loading && tasks.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Material Pickup Tasks
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Task ID</TableCell>
              <TableCell>Production Order</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Materials</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tasks.map((task) => (
              <TableRow key={task.id}>
                <TableCell>#{task.id}</TableCell>
                <TableCell>#{task.order_id}</TableCell>
                <TableCell>
                  <Chip
                    label={task.priority}
                    color={task.priority === 'urgent' ? 'error' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {task.route_card?.materials.length} items
                </TableCell>
                <TableCell>
                  {task.route_card?.current_location || 'Warehouse'}
                </TableCell>
                <TableCell>
                  <Chip
                    label={task.status}
                    color={
                      task.status === 'completed'
                        ? 'success'
                        : task.status === 'in_progress'
                        ? 'warning'
                        : 'default'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handlePickupClick(task)}
                  >
                    Confirm Pickup
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Confirm Material Pickup - Order #{selectedTask?.order_id}
        </DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" sx={{ mb: 2 }}>
            Please verify the following materials before confirming pickup:
          </Typography>
          
          <List>
            {selectedTask?.route_card?.materials.map((material, index) => (
              <React.Fragment key={material.item_id}>
                {index > 0 && <Divider />}
                <ListItem>
                  <ListItemText
                    primary={`Item #${material.item_id}`}
                    secondary={`${material.quantity} ${material.unit}`}
                  />
                </ListItem>
              </React.Fragment>
            ))}
          </List>

          {selectedTask?.route_card?.workstations[0] && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" color="primary" gutterBottom>
                Next Destination:
              </Typography>
              <Typography variant="body1">
                {selectedTask.route_card.workstations[0].name}
              </Typography>
              {selectedTask.route_card.workstations[0].description && (
                <Typography variant="body2" color="text.secondary">
                  {selectedTask.route_card.workstations[0].description}
                </Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmPickup}
            variant="contained"
            color="primary"
          >
            Confirm Pickup
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default MaterialPickupPage;
