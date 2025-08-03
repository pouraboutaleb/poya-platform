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
  Checkbox,
  FormControlLabel
} from '@mui/material';
import {
  fetchPreparationTasks,
  markTaskPrepared
} from '../../store/materialPreparationSlice';

const MaterialPreparationPage = () => {
  const dispatch = useDispatch();
  const { tasks, loading, error } = useSelector(state => state.materialPreparation);
  const [selectedTask, setSelectedTask] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [checkedMaterials, setCheckedMaterials] = useState({});

  useEffect(() => {
    dispatch(fetchPreparationTasks());
    // Refresh the list every 5 minutes
    const interval = setInterval(() => {
      dispatch(fetchPreparationTasks());
    }, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [dispatch]);

  const handlePrepareClick = (task) => {
    setSelectedTask(task);
    setCheckedMaterials({});
    setDialogOpen(true);
  };

  const handleMaterialCheck = (materialId) => {
    setCheckedMaterials(prev => ({
      ...prev,
      [materialId]: !prev[materialId]
    }));
  };

  const handleConfirmPreparation = async () => {
    if (selectedTask) {
      await dispatch(markTaskPrepared(selectedTask.id));
      setDialogOpen(false);
      setSelectedTask(null);
    }
  };

  const allMaterialsChecked = (materials) => {
    return materials.every(m => checkedMaterials[m.item_id]);
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
        Material Preparation Tasks
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
              <TableCell>Required Materials</TableCell>
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
                    onClick={() => handlePrepareClick(task)}
                  >
                    Mark as Prepared
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
          Prepare Materials for Production Order #{selectedTask?.order_id}
        </DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom>
            Please confirm that all materials are prepared:
          </Typography>
          <List>
            {selectedTask?.route_card?.materials.map((material) => (
              <ListItem key={material.item_id}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={!!checkedMaterials[material.item_id]}
                      onChange={() => handleMaterialCheck(material.item_id)}
                    />
                  }
                  label={
                    <ListItemText
                      primary={`Item #${material.item_id}`}
                      secondary={`${material.quantity} ${material.unit}`}
                    />
                  }
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmPreparation}
            variant="contained"
            color="primary"
            disabled={
              !selectedTask?.route_card?.materials ||
              !allMaterialsChecked(selectedTask.route_card.materials)
            }
          >
            Confirm Materials Prepared
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default MaterialPreparationPage;
