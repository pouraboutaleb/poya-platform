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
  Chip
} from '@mui/material';
import {
  fetchProductionOrders,
  setSelectedOrder
} from '../../store/routeCardSlice';
import RouteCardDialog from '../components/molecules/RouteCardDialog';

const ProductionPage = () => {
  const dispatch = useDispatch();
  const { productionOrders, loading, error } = useSelector(state => state.routeCards);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchProductionOrders());
  }, [dispatch]);

  const handleDefineRoute = (order) => {
    dispatch(setSelectedOrder(order));
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
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
        Production Orders
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Item</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Required Date</TableCell>
              <TableCell>Route Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {productionOrders.map((order) => (
              <TableRow key={order.id}>
                <TableCell>#{order.id}</TableCell>
                <TableCell>
                  {order.item ? order.item.name : `Item #${order.item_id}`}
                </TableCell>
                <TableCell>{order.quantity}</TableCell>
                <TableCell>
                  <Chip
                    label={order.priority}
                    color={order.priority === 'urgent' ? 'error' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {order.required_date
                    ? new Date(order.required_date).toLocaleDateString()
                    : 'Not set'}
                </TableCell>
                <TableCell>
                  {order.route_card ? (
                    <Chip
                      label={order.route_card.status}
                      color={order.route_card.status === 'confirmed' ? 'success' : 'warning'}
                      size="small"
                    />
                  ) : (
                    <Chip label="No Route" size="small" />
                  )}
                </TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleDefineRoute(order)}
                    disabled={order.route_card?.status === 'confirmed'}
                  >
                    {order.route_card ? 'View Route' : 'Define Route'}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <RouteCardDialog
        open={dialogOpen}
        onClose={handleDialogClose}
      />
    </Container>
  );
};

export default ProductionPage;
