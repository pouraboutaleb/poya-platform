import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container,
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Check as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { updateWarehouseRequest } from '../../store/warehouseRequestSlice';

const statusColors = {
  draft: 'default',
  submitted: 'info',
  processing: 'warning',
  completed: 'success',
  cancelled: 'error',
};

const priorityColors = {
  low: 'default',
  normal: 'info',
  high: 'warning',
  urgent: 'error',
};

const WarehouseRequestDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  
  const { requests, loading, error } = useSelector((state) => state.warehouseRequests);
  const request = requests.find(r => r.id === parseInt(id, 10));
  
  const [dialogState, setDialogState] = useState({
    open: false,
    type: null,
    itemId: null,
    remarks: '',
  });

  useEffect(() => {
    if (!request) {
      // If we don't have the request data, fetch it
      // TODO: Implement fetchWarehouseRequestById
    }
  }, [id, request]);

  const handleAction = (type, itemId) => {
    setDialogState({
      open: true,
      type,
      itemId,
      remarks: '',
    });
  };

  const handleDialogClose = () => {
    setDialogState({
      open: false,
      type: null,
      itemId: null,
      remarks: '',
    });
  };

  const handleDialogSubmit = async () => {
    const { type, itemId, remarks } = dialogState;
    const item = request.request_items.find(i => i.id === itemId);
    
    let updatedItems = request.request_items.map(i => {
      if (i.id === itemId) {
        let status;
        switch (type) {
          case 'fulfill':
            status = 'ready';
            break;
          case 'shortage':
            status = 'backordered';
            break;
          case 'mismatch':
            status = 'pending';
            break;
          default:
            status = i.status;
        }
        return { ...i, status, remarks };
      }
      return i;
    });

    await dispatch(updateWarehouseRequest({
      id: request.id,
      data: {
        request_items: updatedItems,
        status: type === 'fulfill' ? 'processing' : request.status,
      },
    }));

    handleDialogClose();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" mt={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (!request) {
    return (
      <Container>
        <Alert severity="error">Request not found</Alert>
      </Container>
    );
  }

  const getDialogTitle = () => {
    switch (dialogState.type) {
      case 'fulfill':
        return 'تأیید و آماده‌سازی';
      case 'shortage':
        return 'اعلام کسری';
      case 'mismatch':
        return 'گزارش عدم تطابق موجودی';
      default:
        return '';
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/warehouse-requests')}
          sx={{ mb: 3 }}
        >
          Back to List
        </Button>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error.detail || 'An error occurred'}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h5">
                  Request #{request.id} - {request.project_name}
                </Typography>
                <Box>
                  <Chip
                    label={request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                    color={statusColors[request.status]}
                    sx={{ mr: 1 }}
                  />
                  <Chip
                    label={request.priority.charAt(0).toUpperCase() + request.priority.slice(1)}
                    color={priorityColors[request.priority]}
                  />
                </Box>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="textSecondary">
                    Created By
                  </Typography>
                  <Typography variant="body1">
                    {request.created_by_name}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="textSecondary">
                    Created Date
                  </Typography>
                  <Typography variant="body1">
                    {new Date(request.created_at).toLocaleDateString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="textSecondary">
                    Requested Delivery Date
                  </Typography>
                  <Typography variant="body1">
                    {request.requested_delivery_date
                      ? new Date(request.requested_delivery_date).toLocaleDateString()
                      : 'Not specified'}
                  </Typography>
                </Grid>
                {request.description && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">
                      Description
                    </Typography>
                    <Typography variant="body1">
                      {request.description}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" mb={2}>
                Requested Items
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Item</TableCell>
                      <TableCell align="right">Requested Quantity</TableCell>
                      <TableCell align="right">Fulfilled Quantity</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Remarks</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {request.request_items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>
                          {item.item.name} ({item.item.item_code})
                        </TableCell>
                        <TableCell align="right">{item.quantity_requested}</TableCell>
                        <TableCell align="right">{item.quantity_fulfilled || 0}</TableCell>
                        <TableCell>
                          <Chip
                            label={item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                            color={
                              item.status === 'ready'
                                ? 'success'
                                : item.status === 'backordered'
                                ? 'error'
                                : 'default'
                            }
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{item.remarks}</TableCell>
                        <TableCell align="right">
                          <Button
                            startIcon={<CheckIcon />}
                            color="success"
                            size="small"
                            onClick={() => handleAction('fulfill', item.id)}
                            sx={{ mr: 1 }}
                          >
                            تأیید و آماده‌سازی
                          </Button>
                          <Button
                            startIcon={<WarningIcon />}
                            color="warning"
                            size="small"
                            onClick={() => handleAction('shortage', item.id)}
                            sx={{ mr: 1 }}
                          >
                            اعلام کسری
                          </Button>
                          <Button
                            startIcon={<ErrorIcon />}
                            color="error"
                            size="small"
                            onClick={() => handleAction('mismatch', item.id)}
                          >
                            گزارش عدم تطابق
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>

        <Dialog open={dialogState.open} onClose={handleDialogClose}>
          <DialogTitle>{getDialogTitle()}</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Remarks"
              fullWidth
              multiline
              rows={4}
              value={dialogState.remarks}
              onChange={(e) => setDialogState(prev => ({ ...prev, remarks: e.target.value }))}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDialogClose}>Cancel</Button>
            <Button onClick={handleDialogSubmit} variant="contained" color="primary">
              Submit
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default WarehouseRequestDetailPage;
