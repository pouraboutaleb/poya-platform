import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  CircularProgress,
  Alert,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers';
import { useState } from 'react';
import {
  fetchOrderById,
  updateOrderStatus,
  selectSelectedOrder,
  selectOrdersLoading,
  selectOrdersError
} from '../../store/orderSlice';

const OrderDetailPage = () => {
  const { orderId } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const order = useSelector(selectSelectedOrder);
  const loading = useSelector(selectOrdersLoading);
  const error = useSelector(selectOrdersError);

  const [updateDialogOpen, setUpdateDialogOpen] = useState(false);
  const [updateData, setUpdateData] = useState({
    status: '',
    priority: '',
    quantity: '',
    remarks: '',
    required_date: null
  });

  useEffect(() => {
    dispatch(fetchOrderById(orderId));
  }, [dispatch, orderId]);

  useEffect(() => {
    if (order) {
      setUpdateData({
        status: order.status || '',
        priority: order.priority || '',
        quantity: order.quantity || '',
        remarks: order.remarks || '',
        required_date: order.required_date ? new Date(order.required_date) : null
      });
    }
  }, [order]);

  const handleUpdateClick = () => {
    setUpdateDialogOpen(true);
  };

  const handleUpdateClose = () => {
    setUpdateDialogOpen(false);
  };

  const handleUpdateSubmit = () => {
    dispatch(updateOrderStatus({
      orderId: order.id,
      updateData: {
        ...updateData,
        quantity: Number(updateData.quantity)
      }
    })).then(() => {
      setUpdateDialogOpen(false);
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: 'default',
      submitted: 'info',
      in_progress: 'warning',
      completed: 'success',
      cancelled: 'error'
    };
    return colors[status] || 'default';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!order) {
    return (
      <Container>
        <Alert severity="info">Order not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4">
          Order #{order.id}
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpdateClick}
        >
          Update Order
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Order Details */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Order Details
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Type
                </Typography>
                <Chip
                  label={order.order_type}
                  color={order.order_type === 'production' ? 'primary' : 'secondary'}
                  sx={{ mt: 1 }}
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Status
                </Typography>
                <Chip
                  label={order.status}
                  color={getStatusColor(order.status)}
                  sx={{ mt: 1 }}
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Priority
                </Typography>
                <Typography>{order.priority}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Quantity
                </Typography>
                <Typography>{order.quantity}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">
                  Required Date
                </Typography>
                <Typography>
                  {order.required_date
                    ? new Date(order.required_date).toLocaleDateString()
                    : 'Not set'}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">
                  Remarks
                </Typography>
                <Typography>{order.remarks || 'No remarks'}</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Warehouse Request Details */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Related Warehouse Request
            </Typography>
            {order.warehouse_request_item ? (
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Request ID
                  </Typography>
                  <Typography>
                    #{order.warehouse_request_item.request_id}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Requested Quantity
                  </Typography>
                  <Typography>
                    {order.warehouse_request_item.quantity}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Status
                  </Typography>
                  <Typography>
                    {order.warehouse_request_item.status}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Remarks
                  </Typography>
                  <Typography>
                    {order.warehouse_request_item.remarks || 'No remarks'}
                  </Typography>
                </Grid>
              </Grid>
            ) : (
              <Typography color="text.secondary">
                No related warehouse request
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Update Dialog */}
      <Dialog open={updateDialogOpen} onClose={handleUpdateClose}>
        <DialogTitle>Update Order</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={updateData.status}
                  label="Status"
                  onChange={(e) => setUpdateData({ ...updateData, status: e.target.value })}
                >
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="submitted">Submitted</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={updateData.priority}
                  label="Priority"
                  onChange={(e) => setUpdateData({ ...updateData, priority: e.target.value })}
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="normal">Normal</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Quantity"
                type="number"
                value={updateData.quantity}
                onChange={(e) => setUpdateData({ ...updateData, quantity: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <DatePicker
                label="Required Date"
                value={updateData.required_date}
                onChange={(date) => setUpdateData({ ...updateData, required_date: date })}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Remarks"
                multiline
                rows={4}
                value={updateData.remarks}
                onChange={(e) => setUpdateData({ ...updateData, remarks: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleUpdateClose}>Cancel</Button>
          <Button onClick={handleUpdateSubmit} variant="contained" color="primary">
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default OrderDetailPage;
