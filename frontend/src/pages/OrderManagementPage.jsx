import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Container,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  fetchOrders,
  selectFilteredOrders,
  selectOrdersLoading,
  selectOrdersError,
  selectOrderFilters,
  setTypeFilter,
  setStatusFilter
} from '../../store/orderSlice';

const OrderManagementPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const orders = useSelector(selectFilteredOrders);
  const loading = useSelector(selectOrdersLoading);
  const error = useSelector(selectOrdersError);
  const filters = useSelector(selectOrderFilters);

  useEffect(() => {
    dispatch(fetchOrders());
  }, [dispatch]);

  const handleTypeFilterChange = (event) => {
    dispatch(setTypeFilter(event.target.value));
  };

  const handleStatusFilterChange = (event) => {
    dispatch(setStatusFilter(event.target.value));
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

  const handleRowClick = (orderId) => {
    navigate(`/orders/${orderId}`);
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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Order Management
      </Typography>

      {/* Filters */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Order Type</InputLabel>
            <Select
              value={filters.type}
              label="Order Type"
              onChange={handleTypeFilterChange}
            >
              <MenuItem value="all">All Types</MenuItem>
              <MenuItem value="procurement">Procurement</MenuItem>
              <MenuItem value="production">Production</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status}
              label="Status"
              onChange={handleStatusFilterChange}
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="submitted">Submitted</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="cancelled">Cancelled</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {/* Orders Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Required Date</TableCell>
              <TableCell>Created At</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.map((order) => (
              <TableRow
                key={order.id}
                hover
                onClick={() => handleRowClick(order.id)}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell>#{order.id}</TableCell>
                <TableCell>
                  <Chip
                    label={order.order_type}
                    color={order.order_type === 'production' ? 'primary' : 'secondary'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={order.status}
                    color={getStatusColor(order.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{order.priority}</TableCell>
                <TableCell>{order.quantity}</TableCell>
                <TableCell>
                  {order.required_date
                    ? new Date(order.required_date).toLocaleDateString()
                    : 'Not set'}
                </TableCell>
                <TableCell>
                  {new Date(order.created_at).toLocaleDateString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default OrderManagementPage;
