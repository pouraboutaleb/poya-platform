import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Typography,
  Alert,
  Box
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { createRouteCard, confirmRouteCard } from '../../store/routeCardSlice';

const RouteCardDialog = ({ open, onClose }) => {
  const dispatch = useDispatch();
  const selectedOrder = useSelector(state => state.routeCards.selectedOrder);
  const [error, setError] = useState(null);
  
  const [materials, setMaterials] = useState([]);
  const [workstations, setWorkstations] = useState([]);
  const [newMaterial, setNewMaterial] = useState({
    item_id: '',
    quantity: '',
    unit: ''
  });
  const [newWorkstation, setNewWorkstation] = useState({
    name: '',
    description: '',
    estimated_hours: '',
    is_subcontractor: false
  });

  useEffect(() => {
    if (selectedOrder?.route_card) {
      setMaterials(selectedOrder.route_card.materials);
      setWorkstations(selectedOrder.route_card.workstations);
    } else {
      setMaterials([]);
      setWorkstations([]);
    }
  }, [selectedOrder]);

  const handleAddMaterial = () => {
    if (newMaterial.item_id && newMaterial.quantity && newMaterial.unit) {
      setMaterials([...materials, { ...newMaterial }]);
      setNewMaterial({ item_id: '', quantity: '', unit: '' });
    }
  };

  const handleRemoveMaterial = (index) => {
    setMaterials(materials.filter((_, i) => i !== index));
  };

  const handleAddWorkstation = () => {
    if (newWorkstation.name && newWorkstation.estimated_hours) {
      setWorkstations([...workstations, { ...newWorkstation }]);
      setNewWorkstation({
        name: '',
        description: '',
        estimated_hours: '',
        is_subcontractor: false
      });
    }
  };

  const handleRemoveWorkstation = (index) => {
    setWorkstations(workstations.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (!materials.length || !workstations.length) {
      setError('Please add at least one material and one workstation');
      return;
    }

    const routeCardData = {
      order_id: selectedOrder.id,
      materials,
      workstations,
      estimated_time: workstations.reduce(
        (sum, station) => sum + parseFloat(station.estimated_hours),
        0
      )
    };

    try {
      await dispatch(createRouteCard(routeCardData)).unwrap();
      onClose();
    } catch (error) {
      setError(error.message);
    }
  };

  const handleConfirm = async () => {
    try {
      await dispatch(confirmRouteCard(selectedOrder.route_card.id)).unwrap();
      onClose();
    } catch (error) {
      setError(error.message);
    }
  };

  const isReadOnly = selectedOrder?.route_card?.status === 'confirmed';

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {selectedOrder ? `Route Card - Order #${selectedOrder.id}` : 'Route Card'}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Materials Section */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Materials (MTO)
            </Typography>
            <List>
              {materials.map((material, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={`Item #${material.item_id}`}
                    secondary={`${material.quantity} ${material.unit}`}
                  />
                  {!isReadOnly && (
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={() => handleRemoveMaterial(index)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  )}
                </ListItem>
              ))}
            </List>
            {!isReadOnly && (
              <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                <TextField
                  label="Item ID"
                  value={newMaterial.item_id}
                  onChange={(e) =>
                    setNewMaterial({ ...newMaterial, item_id: e.target.value })
                  }
                  size="small"
                />
                <TextField
                  label="Quantity"
                  value={newMaterial.quantity}
                  onChange={(e) =>
                    setNewMaterial({ ...newMaterial, quantity: e.target.value })
                  }
                  size="small"
                />
                <TextField
                  label="Unit"
                  value={newMaterial.unit}
                  onChange={(e) =>
                    setNewMaterial({ ...newMaterial, unit: e.target.value })
                  }
                  size="small"
                />
                <IconButton color="primary" onClick={handleAddMaterial}>
                  <AddIcon />
                </IconButton>
              </Box>
            )}
          </Grid>

          {/* Workstations Section */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Production Route
            </Typography>
            <List>
              {workstations.map((station, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={station.name}
                    secondary={`${station.estimated_hours} hours${
                      station.description ? ` - ${station.description}` : ''
                    }`}
                  />
                  {!isReadOnly && (
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={() => handleRemoveWorkstation(index)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  )}
                </ListItem>
              ))}
            </List>
            {!isReadOnly && (
              <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                <TextField
                  label="Workstation Name"
                  value={newWorkstation.name}
                  onChange={(e) =>
                    setNewWorkstation({ ...newWorkstation, name: e.target.value })
                  }
                  size="small"
                />
                <TextField
                  label="Est. Hours"
                  type="number"
                  value={newWorkstation.estimated_hours}
                  onChange={(e) =>
                    setNewWorkstation({
                      ...newWorkstation,
                      estimated_hours: e.target.value
                    })
                  }
                  size="small"
                />
                <TextField
                  label="Description"
                  value={newWorkstation.description}
                  onChange={(e) =>
                    setNewWorkstation({
                      ...newWorkstation,
                      description: e.target.value
                    })
                  }
                  size="small"
                />
                <IconButton color="primary" onClick={handleAddWorkstation}>
                  <AddIcon />
                </IconButton>
              </Box>
            )}
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        {!isReadOnly && (
          <>
            <Button onClick={handleSubmit} variant="contained" color="primary">
              Save Route
            </Button>
            {selectedOrder?.route_card && (
              <Button onClick={handleConfirm} variant="contained" color="success">
                Confirm Route
              </Button>
            )}
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default RouteCardDialog;
